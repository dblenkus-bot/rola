"""Fixtures for integration tests."""

import pytest


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Keep media written by tests outside the source tree."""
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture(autouse=True)
def portable_api_settings(request, settings):
    """Run reusable-domain tests against their portable URL and DRF configuration."""
    if request.module.__name__.startswith(("rolca.", "tests.")):
        settings.ROOT_URLCONF = "tests.urls"
        settings.STORAGES = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
