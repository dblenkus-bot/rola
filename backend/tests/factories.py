"""Build accounts and submissions for portable and host integration tests."""

import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from rolca.core.models import File, Submission


def create_user(name: str, *, superuser: bool = False):
    """Create an active account through its configured username field."""
    model = get_user_model()
    email = f"{name}@example.org"
    fields = {model.USERNAME_FIELD: email if model.USERNAME_FIELD == "email" else name}
    fields.update(email=email, is_active=True)
    manager_method = (
        model.objects.create_superuser if superuser else model.objects.create_user
    )
    return manager_method(password="test-only-passphrase-A9!", **fields)


def photo(user, name="photo.jpg"):
    """Create a stored JPEG belonging to the given account."""
    data = io.BytesIO()
    Image.new("RGB", (800, 600), "red").save(data, "JPEG")
    return File.objects.create(
        user=user,
        file=SimpleUploadedFile(name, data.getvalue(), content_type="image/jpeg"),
    )


def payload(world, **changes):
    """Build a submission request using an account-owned photograph."""
    result = {
        "title": "Photo",
        "theme": world.theme.pk,
        "author": {"id": world.author.pk},
        "files": [{"id": photo(world.owner).pk}],
    }
    result.update(changes)
    return result


def submitted(world, **changes):
    """Create a submission in the fixture contest."""
    data = dict(
        user=world.owner, title="Original", theme=world.theme, author=world.author
    )
    data.update(changes)
    return Submission.objects.create(**data)
