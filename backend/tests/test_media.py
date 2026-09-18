"""Exercise photograph storage and thumbnail generation."""

import pytest
from PIL import Image

from tests.factories import create_user, photo

pytestmark = pytest.mark.django_db


def test_upload_creates_jpeg_thumbnail():
    user = create_user("photographer")
    image = photo(user)
    with image.thumbnail.open("rb") as source, Image.open(source) as thumb:
        assert thumb.size == (400, 300)
        assert thumb.format == "JPEG"
