"""Settings for DFR User application."""

from datetime import timedelta

from django.conf import settings


class DrfUserSettings:
    """Provides settings as defaults."""

    @property
    def TOKEN_EXPIRES_SECONDS(self) -> timedelta:
        """Return the allowed lifespan of a authentication token as timedelta."""
        seconds = getattr(settings, "DRF_USER_TOKEN_EXPIRES_SECONDS", 172_800)

        return timedelta(seconds=seconds)

    @property
    def RESET_TOKEN_EXPIRES_SECONDS(self) -> timedelta:
        """Return the allowed lifespan of a password reset token as timedelta."""
        seconds = getattr(settings, "DRF_USER_RESET_TOKEN_EXPIRES_SECONDS", 86_400)

        return timedelta(seconds=seconds)

    @property
    def ACTIVATION_TOKEN_EXPIRES_SECONDS(self) -> timedelta:
        """Return the allowed lifespan of a password reset token as timedelta."""
        seconds = getattr(
            settings, "DRF_USER_ACTIVATION_TOKEN_EXPIRES_SECONDS", 302_400
        )

        return timedelta(seconds=seconds)

    @property
    def APP_NAME(self) -> str:
        """Return name of the app."""
        return str(getattr(settings, "DRF_USER_APP_NAME", "DRF User"))


drf_user_settings = DrfUserSettings()
