"""Authenticate expiring account tokens."""

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
