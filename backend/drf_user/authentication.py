"""Authenticate expiring account tokens."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication, exceptions

from .models import Token


class TokenAuthentication(authentication.TokenAuthentication):
    """Authenticate the existing ``Authorization: Token`` protocol."""

    model = Token

    def authenticate_credentials(self, key):
        """Reject missing, expired and inactive-account credentials."""
        try:
            token = Token.objects.select_related("user").get(key=key)
        except Token.DoesNotExist as error:
            raise exceptions.AuthenticationFailed("Invalid token") from error
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted")
        if token.is_expired:
            raise exceptions.AuthenticationFailed("Token has expired")
        return token.user, token


class TokenAuthenticationSchema(OpenApiAuthenticationExtension):
    """Describe the expiring token header in the API contract."""

    target_class = "drf_user.authentication.TokenAuthentication"
    name = "tokenAuth"

    def get_security_definition(self, auto_schema):
        """Describe the required authorization header."""
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Use the value Token followed by a space and the login token.",
        }
