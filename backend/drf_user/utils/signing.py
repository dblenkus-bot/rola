"""Create and validate signed account email tokens."""

import logging
from urllib.parse import urlencode

from django.conf import settings

from django.core import signing
from django.template.loader import render_to_string
from rest_framework import exceptions

from drf_user.models import User
from drf_user.settings import drf_user_settings

logger = logging.getLogger(__name__)

USER_ACTIVATION_SALT = "user_activation"
PASSWORD_RESET_SALT = "password_reset"


def _generate_token(token_generator, user, salt):
    # Create a signed token, containing the user identifier and timestamp.
    return signing.dumps(obj=token_generator(user), salt=salt)


def generate_activation_token(user):
    def token_generator(user):
        return user.email

    return _generate_token(token_generator, user, USER_ACTIVATION_SALT)


def generate_reset_token(user):
    def token_generator(user):
        return {
            "email": user.email,
            "counter": user.password_reset_counter,
        }

    return _generate_token(token_generator, user, PASSWORD_RESET_SALT)


def _send_user_email(user, request, template, path, token):
    base_url = settings.ROLA_FRONTEND_URL.rstrip("/") or request.build_absolute_uri(
        "/"
    ).rstrip("/")
    context = {
        "first_name": user.first_name or "",
        "app_name": drf_user_settings.APP_NAME,
        "url": f"{base_url}{path}?{urlencode({'token': token})}",
    }
    subject = "".join(
        render_to_string(f"drf_user/{template}/email_subject.txt", context).splitlines()
    )
    body = render_to_string(f"drf_user/{template}/email_body.txt", context)
    html_body = render_to_string(f"drf_user/{template}/email_body.html", context)
    try:
        user.email_user(subject, body, html_message=html_body)
    except Exception:
        logger.error("Unable to send account email.")


def send_activation_email(user, request):
    """Send an activation link pointing to the configured frontend."""
    _send_user_email(
        user,
        request,
        "registration",
        "/register/activate",
        generate_activation_token(user),
    )


def send_reset_email(user, request):
    """Send a recovery link pointing to the configured frontend."""
    _send_user_email(
        user, request, "password_reset", "/password-reset", generate_reset_token(user)
    )


def validate_activation_token(token):
    """Validate activation token and return referenced user."""
    try:
        email = signing.loads(
            token,
            salt=USER_ACTIVATION_SALT,
            max_age=drf_user_settings.ACTIVATION_TOKEN_EXPIRES_SECONDS.total_seconds(),
        )
        user = User.objects.get(email=email, is_active=False)
    except (signing.BadSignature, User.DoesNotExist):
        raise exceptions.ValidationError("Bad token.")

    return user


def validate_reset_token(token):
    """Validate password reset token and return referenced user."""
    try:
        data = signing.loads(
            token,
            salt=PASSWORD_RESET_SALT,
            max_age=drf_user_settings.RESET_TOKEN_EXPIRES_SECONDS.total_seconds(),
        )
        user = User.objects.get(
            email=data["email"],
            password_reset_counter=data["counter"],
        )
    except (signing.BadSignature, User.DoesNotExist):
        raise exceptions.ValidationError("Bad token.")

    if not user.is_active:
        raise exceptions.ValidationError("Account is not activated, contact support.")

    return user
