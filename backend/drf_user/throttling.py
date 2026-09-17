"""Apply request limits to credential and email endpoints."""

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView


class AccountThrottle(SimpleRateThrottle):
    """Limit registration and recovery requests by client address."""

    scope = "account"

    def get_cache_key(self, request: Request, view: APIView) -> str:
        """Use the client address even when the caller has a session."""
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class LoginThrottle(AccountThrottle):
    """Limit login attempts by client address."""

    scope = "login"
