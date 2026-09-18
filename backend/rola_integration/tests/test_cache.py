"""Keep login limits shared and browser sessions independent of cache contents."""

from unittest.mock import patch

import pytest
from django.core.cache import caches
from django.core.cache.backends.db import DatabaseCache
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from drf_user.throttling import LoginThrottle
from rola import settings as production_settings
from tests.factories import create_user


@pytest.fixture
def database_cache(settings, db):
    """Create the production cache table in the isolated test database."""
    settings.CACHES = production_settings.CACHES
    settings.SESSION_ENGINE = production_settings.SESSION_ENGINE
    backend = caches["default"]
    assert isinstance(backend, DatabaseCache)
    call_command("createcachetable", verbosity=0)
    backend.clear()
    return backend


def test_login_limit_is_shared_between_cache_instances(database_cache, settings):
    payload = {"email": "unknown@example.org", "password": "Incorrect!73"}
    url = reverse("login")

    with patch.object(LoginThrottle, "THROTTLE_RATES", {"login": "2/minute"}):
        assert APIClient().post(url, payload).status_code == 400

        settings.CACHES = production_settings.CACHES
        assert caches["default"] is not database_cache
        assert APIClient().post(url, payload).status_code == 400
        assert APIClient().post(url, payload).status_code == 429


def test_admin_session_survives_clearing_the_cache(database_cache):
    user = create_user("organizer", superuser=True)
    browser = Client()
    browser.force_login(user)
    assert browser.get(reverse("admin:index")).status_code == 200

    database_cache.clear()

    returning_browser = Client()
    returning_browser.cookies = browser.cookies
    response = returning_browser.get(reverse("admin:index"))
    assert response.status_code == 200
    assert response.wsgi_request.user.pk == user.pk
