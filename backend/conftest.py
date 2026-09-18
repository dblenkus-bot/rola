"""Fixtures for integration tests."""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from rolca.core.models import Author, Contest, Theme
from tests.factories import create_user


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Keep media written by tests outside the source tree."""
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def portable_api_settings(settings):
    """Use standalone domain URLs and filesystem storage for portable tests."""
    settings.ROOT_URLCONF = "tests.urls"
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }


@pytest.fixture
def world():
    """Create a contest, its authors and an authenticated submission client."""
    owner = create_user("owner")
    other = create_user("other")
    admin = create_user("admin", superuser=True)
    now = timezone.now()
    contest = Contest.objects.create(
        user=admin,
        title="Salon",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        publish_date=now + timedelta(days=2),
    )
    theme = Theme.objects.create(contest=contest, title="Nature", n_photos=4)
    author = Author.objects.create(
        user=owner, first_name="Alice", last_name="Photographer"
    )
    other_author = Author.objects.create(user=other, first_name="Other")
    client = APIClient()
    client.force_authenticate(owner)
    return SimpleNamespace(
        owner=owner,
        other=other,
        admin=admin,
        contest=contest,
        theme=theme,
        author=author,
        other_author=other_author,
        client=client,
    )
