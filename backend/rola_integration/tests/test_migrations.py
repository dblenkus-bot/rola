"""Preserve real host data while replacing its historical migration graph."""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.test import override_settings
from django.utils import timezone

from rola_integration.migration_settings import (
    LEGACY_MIGRATION_MODULES,
    PORTABLE_MIGRATIONS,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def legacy_database():
    """Reconstruct a deployed schema with data and no optional backup app tables."""
    executor = MigrationExecutor(connection)
    executor.migrate([(app, None) for app in LEGACY_MIGRATION_MODULES])
    recorder = MigrationRecorder(connection)
    for key in list(recorder.applied_migrations()):
        if key[0] in LEGACY_MIGRATION_MODULES:
            recorder.record_unapplied(*key)
    with override_settings(MIGRATION_MODULES=LEGACY_MIGRATION_MODULES):
        executor = MigrationExecutor(connection)
        targets = [
            ("core", "0021_auto_20210208_1803"),
            ("rating", "0004_submissionreward_label"),
            ("payment", "0002_existing_payments"),
        ]
        executor.migrate(targets)
        historical = executor.loader.project_state(targets).apps
        user = historical.get_model("drf_user", "User").objects.create(
            email="owner@example.org", password="!", is_active=True
        )
        template = historical.get_model("drf_user", "Email").objects.create(
            subject="Thank you", body="Your photos were submitted"
        )
        now = timezone.now()
        contest = historical.get_model("core", "Contest").objects.create(
            user_id=user.pk,
            title="Existing contest",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            publish_date=now + timedelta(days=2),
            confirmation_email_id=template.pk,
        )
        author = historical.get_model("core", "Author").objects.create(
            user_id=user.pk, first_name="Existing", last_name="Author"
        )
        theme = historical.get_model("core", "Theme").objects.create(
            contest_id=contest.pk, title="Nature", n_photos=4
        )
        submission = historical.get_model("core", "Submission").objects.create(
            author_id=author.pk,
            theme_id=theme.pk,
            user_id=user.pk,
            title="Existing photo",
        )
        group = historical.get_model("core", "SubmissionSet").objects.create(
            user_id=user.pk, author_id=author.pk, contest_id=contest.pk
        )
        group.submissions.add(submission)
        historical.get_model("payment", "Payment").objects.create(
            submissionset_id=group.pk, paid=True
        )
    assert "backup_filebackup" not in connection.introspection.table_names()
    yield {
        "contest": contest.pk,
        "template": template.pk,
        "user": user.pk,
        "group": group.pk,
    }
    recorder.record_unapplied("core", "9999_unknown")
    recorded_portable = PORTABLE_MIGRATIONS & set(recorder.applied_migrations())
    if recorded_portable != PORTABLE_MIGRATIONS:
        for key in recorded_portable:
            recorder.record_unapplied(*key)
        call_command("upgrade_legacy_rolca", verbosity=0)


def test_upgrade_preserves_template_links_and_existing_data(legacy_database):
    from rola_integration.models import ContestNotification
    from rolca.core.models import Contest, SubmissionSet
    from rolca.payment.models import Payment

    with pytest.raises(CommandError, match="upgrade_legacy_rolca"):
        call_command("migrate", verbosity=0)
    call_command("upgrade_legacy_rolca", verbosity=0)
    configuration = ContestNotification.objects.get(
        contest_id=legacy_database["contest"]
    )
    assert configuration.confirmation_email_id == legacy_database["template"]
    assert Contest.objects.get().user_id == legacy_database["user"]
    assert SubmissionSet.objects.get().pk == legacy_database["group"]
    assert SubmissionSet.objects.get().submissions.get().title == "Existing photo"
    assert Payment.objects.get().paid
    assert "backup_filebackup" in connection.introspection.table_names()
    assert (
        set(MigrationRecorder(connection).applied_migrations()) >= PORTABLE_MIGRATIONS
    )
    call_command("upgrade_legacy_rolca", verbosity=0)
    call_command("migrate", verbosity=0)
    assert ContestNotification.objects.count() == 1


def test_upgrade_refuses_unknown_history_before_changing_schema(legacy_database):
    MigrationRecorder(connection).record_applied("core", "9999_unknown")
    with pytest.raises(CommandError, match="Unrecognized legacy migrations"):
        call_command("upgrade_legacy_rolca", verbosity=0)
    assert (
        "rola_integration_contestnotification"
        not in connection.introspection.table_names()
    )


def test_interrupted_upgrade_can_resume_after_schema_validation_failure(
    legacy_database,
):
    with override_settings(MIGRATION_MODULES=LEGACY_MIGRATION_MODULES):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE core_contest ADD COLUMN unexpected text")
    try:
        with pytest.raises(CommandError, match="Columns in 'core_contest'"):
            call_command("upgrade_legacy_rolca", verbosity=0)
        assert not PORTABLE_MIGRATIONS & set(
            MigrationRecorder(connection).applied_migrations()
        )
    finally:
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE core_contest DROP COLUMN unexpected")
    call_command("upgrade_legacy_rolca", verbosity=0)
    from rola_integration.models import ContestNotification

    assert (
        ContestNotification.objects.get().confirmation_email_id
        == legacy_database["template"]
    )


def test_partial_portable_recording_is_rejected(legacy_database):
    MigrationRecorder(connection).record_applied("core", "0001_portable")
    with pytest.raises(CommandError, match="only partially recorded"):
        call_command("upgrade_legacy_rolca", verbosity=0)


def test_changed_template_mapping_prevents_legacy_column_removal(legacy_database):
    with override_settings(MIGRATION_MODULES=LEGACY_MIGRATION_MODULES):
        executor = MigrationExecutor(connection)
        executor.migrate([("rola_integration", "0001_initial")])
        historical = executor.loader.project_state(
            [("rola_integration", "0001_initial")]
        ).apps
        Notification = historical.get_model("rola_integration", "ContestNotification")
        Notification.objects.update(confirmation_email_id=None)
    with pytest.raises(RuntimeError, match="were not copied exactly"):
        call_command("upgrade_legacy_rolca", verbosity=0)
    with connection.cursor() as cursor:
        columns = connection.introspection.get_table_description(cursor, "core_contest")
    assert "confirmation_email_id" in {column.name for column in columns}
    Notification.objects.update(confirmation_email_id=legacy_database["template"])
    call_command("upgrade_legacy_rolca", verbosity=0)


def test_unknown_schema_is_rejected_before_upgrade(legacy_database):
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE core_contest ADD COLUMN unexpected text")
    try:
        with pytest.raises(CommandError, match="Columns in 'core_contest'"):
            call_command("upgrade_legacy_rolca", verbosity=0)
        assert (
            "rola_integration_contestnotification"
            not in connection.introspection.table_names()
        )
    finally:
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE core_contest DROP COLUMN unexpected")


@pytest.mark.skipif(
    connection.vendor != "postgresql", reason="PostgreSQL identity validation"
)
def test_missing_generated_primary_key_is_rejected(legacy_database):
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE core_contest ALTER COLUMN id DROP IDENTITY")
    try:
        with pytest.raises(
            CommandError, match="Automatic primary key generation is missing"
        ):
            call_command("upgrade_legacy_rolca", verbosity=0)
        assert not PORTABLE_MIGRATIONS & set(
            MigrationRecorder(connection).applied_migrations()
        )
        assert (
            "rola_integration_contestnotification"
            not in connection.introspection.table_names()
        )
    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE core_contest ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY"
            )
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('core_contest', 'id'), COALESCE(MAX(id), 1)) FROM core_contest"
            )


@pytest.mark.skipif(
    connection.vendor != "postgresql", reason="PostgreSQL serial column validation"
)
def test_pre_identity_serial_primary_key_can_be_adopted(legacy_database):
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE core_contest ALTER COLUMN id DROP IDENTITY")
        cursor.execute(
            "CREATE SEQUENCE core_contest_legacy_id_seq OWNED BY core_contest.id"
        )
        cursor.execute(
            "ALTER TABLE core_contest ALTER COLUMN id SET DEFAULT nextval('core_contest_legacy_id_seq')"
        )
        cursor.execute(
            "SELECT setval('core_contest_legacy_id_seq', COALESCE(MAX(id), 1)) FROM core_contest"
        )
    call_command("upgrade_legacy_rolca", verbosity=0)
    from rolca.core.models import Contest

    now = timezone.now()
    contest = Contest.objects.create(title="New contest", start_date=now, end_date=now)
    assert contest.pk > legacy_database["contest"]
