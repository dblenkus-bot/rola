"""Account fixtures compatible with standard and custom Django user models."""

from django.contrib.auth import get_user_model


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
