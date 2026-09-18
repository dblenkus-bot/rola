"""Verify portable hooks and the absence of host-model assumptions."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.loader import MigrationLoader

from rolca.core.api.serializers import AuthorSerializer
from tests.factories import payload

confirmation_callback = Mock()
pytestmark = pytest.mark.django_db


def test_standalone_migrations_do_not_load_host_apps():
    if get_user_model()._meta.label != "auth.User":
        pytest.skip("This assertion runs in the standard Django user configuration.")
    assert not apps.is_installed("drf_user")
    assert not apps.is_installed("rola_integration")
    assert all(
        key[0] != "drf_user" for key in MigrationLoader(connection).disk_migrations
    )


def test_confirmation_callback_failure_keeps_committed_submission(
    world, settings, django_capture_on_commit_callbacks, caplog
):
    settings.ROLCA_SUBMISSION_CONFIRMATION_CALLBACK = (
        "tests.test_portability.confirmation_callback"
    )
    with (
        patch.object(
            confirmation_callback, "side_effect", RuntimeError("Mail unavailable")
        ),
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = world.client.post("/api/submission/", payload(world), format="json")
    assert response.status_code == 201
    assert "Mail unavailable" in caplog.text


def test_author_email_uses_the_user_models_configured_field():
    request = SimpleNamespace(user=SimpleNamespace(is_superuser=True))
    user = SimpleNamespace(
        contact_email="author@example.org", get_email_field_name=lambda: "contact_email"
    )
    author = SimpleNamespace(user=user, email=None)
    serializer = AuthorSerializer(context={"request": request})
    assert serializer.get_email(author) == "author@example.org"
    del user.contact_email
    assert serializer.get_email(author) is None
