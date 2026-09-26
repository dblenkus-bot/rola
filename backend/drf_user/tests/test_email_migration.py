"""Verify email normalization on existing databases."""

import pytest
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder

MIGRATE_FROM = ("drf_user", "0004_email")
MIGRATE_TO = ("drf_user", "0005_case_insensitive_email")


@pytest.fixture
def old_users(transactional_db):
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    executor.migrate([MIGRATE_FROM])
    users = (
        executor.loader.project_state([MIGRATE_FROM])
        .apps.get_model("drf_user", "User")
        .objects
    )
    try:
        yield users
    finally:
        users.all().delete()
        MigrationExecutor(connection).migrate(targets)


def test_migration_normalizes_addresses_and_enforces_case_insensitive_uniqueness(
    old_users,
):
    user = old_users.create(email="Person.Name+Contest@Example.com", password="!")
    MigrationExecutor(connection).migrate([MIGRATE_TO])
    user.refresh_from_db()
    assert user.email == "person.name+contest@example.com"
    with pytest.raises(IntegrityError), transaction.atomic():
        old_users.create(email="PERSON.NAME+CONTEST@EXAMPLE.COM", password="!")
    old_users.create(email="personname+contest@example.com", password="!")
    old_users.create(email="person.name+other@example.com", password="!")


def test_migration_stops_without_changes_until_duplicates_are_resolved(old_users):
    first = old_users.create(email="Person@Example.com", password="!")
    duplicate = old_users.create(email="person@example.com", password="!")
    other = old_users.create(email="Other@Example.com", password="!")
    before = dict(old_users.values_list("pk", "email"))

    with pytest.raises(RuntimeError, match="Resolve them manually") as error:
        MigrationExecutor(connection).migrate([MIGRATE_TO])

    assert dict(old_users.values_list("pk", "email")) == before
    assert MIGRATE_TO not in MigrationRecorder(connection).applied_migrations()
    assert all(email not in str(error.value) for email in before.values())

    duplicate.email = "different@example.com"
    duplicate.save(update_fields=["email"])
    MigrationExecutor(connection).migrate([MIGRATE_TO])
    assert dict(old_users.values_list("pk", "email")) == {
        first.pk: "person@example.com",
        duplicate.pk: "different@example.com",
        other.pk: "other@example.com",
    }
