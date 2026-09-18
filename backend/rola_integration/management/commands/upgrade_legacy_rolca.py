"""Upgrade and explicitly adopt an existing Rolca database."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder
from django.test import override_settings

from rola_integration.migration_settings import (
    LEGACY_MIGRATION_MODULES,
    PORTABLE_MIGRATIONS,
)


def _column_type(internal_type: str) -> str:
    aliases = {
        "AutoField": "IntegerField",
        "PositiveIntegerField": "IntegerField",
        "BigAutoField": "BigIntegerField",
        "PositiveBigIntegerField": "BigIntegerField",
        "SmallAutoField": "SmallIntegerField",
        "PositiveSmallIntegerField": "SmallIntegerField",
        "EmailField": "CharField",
        "SlugField": "CharField",
        "URLField": "CharField",
        "FileField": "CharField",
        "ImageField": "CharField",
    }
    return aliases.get(internal_type, internal_type)


def _validate_schema(connection, state) -> None:
    models = [
        model
        for model in state.apps.get_models(include_auto_created=True)
        if model._meta.app_label in LEGACY_MIGRATION_MODULES
    ]
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
        for model in models:
            options = model._meta
            table = options.db_table
            if table not in tables:
                raise CommandError(f"Expected legacy table {table!r} is missing.")
            columns = {
                column.name: column
                for column in connection.introspection.get_table_description(
                    cursor, table
                )
            }
            fields = {field.column: field for field in options.local_fields}
            if columns.keys() != fields.keys():
                raise CommandError(
                    f"Columns in {table!r} do not match the portable schema."
                )
            constraints = connection.introspection.get_constraints(cursor, table)
            for name, field in fields.items():
                expected_field = field.target_field if field.is_relation else field
                actual_type = connection.introspection.get_field_type(
                    columns[name].type_code, columns[name]
                )
                auto_type = field.get_internal_type()
                if (
                    connection.vendor == "postgresql"
                    and auto_type in {"AutoField", "BigAutoField", "SmallAutoField"}
                    and actual_type != auto_type
                ):
                    raise CommandError(
                        f"Automatic primary key generation is missing for {table}.{name}."
                    )
                if _column_type(actual_type) != _column_type(
                    expected_field.get_internal_type()
                ):
                    raise CommandError(f"Column type differs for {table}.{name}.")
                if (
                    expected_field.max_length is not None
                    and columns[name].internal_size is not None
                    and expected_field.max_length != columns[name].internal_size
                ):
                    raise CommandError(f"Column length differs for {table}.{name}.")
                if bool(columns[name].null_ok) != field.null:
                    raise CommandError(f"Nullability differs for {table}.{name}.")
                matching = [
                    value
                    for value in constraints.values()
                    if value["columns"] == [name]
                ]
                if field.primary_key and not any(
                    value["primary_key"] for value in matching
                ):
                    raise CommandError(f"Primary key is missing for {table}.{name}.")
                if field.unique and not any(
                    value["unique"] or value["primary_key"] for value in matching
                ):
                    raise CommandError(
                        f"Unique constraint is missing for {table}.{name}."
                    )
                if field.db_index and not any(
                    value["index"] or value["unique"] for value in matching
                ):
                    raise CommandError(f"Index is missing for {table}.{name}.")
                if field.many_to_one or field.one_to_one:
                    target = (
                        field.target_field.model._meta.db_table,
                        field.target_field.column,
                    )
                    if not any(value["foreign_key"] == target for value in matching):
                        raise CommandError(f"Foreign key differs for {table}.{name}.")
            unique_groups = [*options.unique_together]
            unique_groups.extend(
                constraint.fields
                for constraint in options.constraints
                if getattr(constraint, "fields", None)
            )
            for group in unique_groups:
                expected = [options.get_field(name).column for name in group]
                if not any(
                    value["unique"] and value["columns"] == expected
                    for value in constraints.values()
                ):
                    raise CommandError(
                        f"Unique constraint is missing for {table}{tuple(expected)}."
                    )


class Command(BaseCommand):
    """Advance the preserved history and record validated portable baselines."""

    help = "Upgrade an existing Rolca database before running ordinary migrate."

    def add_arguments(self, parser) -> None:
        """Select the database whose historical schema is being adopted."""
        parser.add_argument("--database", default="default", choices=connections)

    def handle(self, *args, **options) -> None:
        """Upgrade recognized histories without recreating existing tables."""
        database = options["database"]
        connection = connections[database]
        recorder = MigrationRecorder(connection)
        applied = set(recorder.applied_migrations())
        normal_modules = {
            key: value
            for key, value in settings.MIGRATION_MODULES.items()
            if key not in LEGACY_MIGRATION_MODULES
        }
        with override_settings(MIGRATION_MODULES=normal_modules):
            portable_loader = MigrationLoader(connection)
            portable_state = portable_loader.project_state()
        if applied >= PORTABLE_MIGRATIONS:
            _validate_schema(connection, portable_state)
            self.stdout.write("Portable Rolca migrations have already been adopted.")
            return
        if PORTABLE_MIGRATIONS & applied:
            raise CommandError(
                "The portable baseline is only partially recorded; restore a consistent backup."
            )
        domain_applied = {key for key in applied if key[0] in LEGACY_MIGRATION_MODULES}
        if not domain_applied:
            raise CommandError(
                "No legacy Rolca history exists. Use 'migrate' for a fresh database."
            )
        modules = {**settings.MIGRATION_MODULES, **LEGACY_MIGRATION_MODULES}
        with override_settings(MIGRATION_MODULES=modules):
            executor = MigrationExecutor(connection)
            known = set(executor.loader.disk_migrations)
            for migration in executor.loader.disk_migrations.values():
                known.update(migration.replaces)
            unknown = domain_applied - known
            if unknown:
                raise CommandError(f"Unrecognized legacy migrations: {sorted(unknown)}")
            executor.loader.check_consistent_history(connection)
            applied_nodes = [
                key
                for key in executor.loader.applied_migrations
                if key in executor.loader.graph.nodes
            ]
            current_state = executor.loader.project_state(applied_nodes)
            _validate_schema(connection, current_state)
            executor.migrate(executor.loader.graph.leaf_nodes())
            executor = MigrationExecutor(connection)
            legacy_state = executor.loader.project_state()
            if executor.migration_plan(executor.loader.graph.leaf_nodes()):
                raise CommandError("The legacy migration history is incomplete.")
        changes = MigrationAutodetector(legacy_state, portable_state).changes(
            graph=portable_loader.graph
        )
        if set(changes) & LEGACY_MIGRATION_MODULES.keys():
            raise CommandError(
                "Legacy and portable model states differ; migration adoption stopped."
            )
        _validate_schema(connection, portable_state)
        with transaction.atomic(using=database):
            for app, name in sorted(PORTABLE_MIGRATIONS):
                recorder.record_applied(app, name)
        self.stdout.write(
            self.style.SUCCESS(
                "Legacy Rolca data preserved and portable migrations adopted."
            )
        )
