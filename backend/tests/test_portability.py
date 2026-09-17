"""Verify portable hooks and the absence of host-model assumptions."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from rolca.core.api.serializers import AuthorSerializer
from tests.test_workflows import payload
from tests.test_workflows import world as world

confirmation_callback = Mock()
pytestmark = pytest.mark.django_db


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
