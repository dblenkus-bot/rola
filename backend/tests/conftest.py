"""Apply the portable domain configuration to cross-app tests."""

import pytest


@pytest.fixture(autouse=True)
def portable_settings(portable_api_settings):
    """Run cross-app tests with standalone URLs and filesystem storage."""
