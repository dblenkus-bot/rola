"""Apply the portable domain configuration to core tests."""

import pytest


@pytest.fixture(autouse=True)
def portable_settings(portable_api_settings):
    """Run domain tests with standalone URLs and filesystem storage."""
