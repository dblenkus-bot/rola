"""Isolate rate limits between account tests."""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_account_rate_limits():
    """Start each account test with an empty throttle cache."""
    cache.clear()
