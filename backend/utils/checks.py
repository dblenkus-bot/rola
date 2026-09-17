"""Validate deployment features that cannot be inferred by Django."""

from django.conf import settings
from django.core.checks import Error, register


@register(deploy=True)
def check_mail_delivery(app_configs, **kwargs):
    """Require delivery configuration before production account registration."""
    backend = settings.MAILERS.get("default", {}).get("BACKEND", "")
    if not settings.DEBUG and backend.endswith(
        ("dummy.EmailBackend", "console.EmailBackend")
    ):
        return [
            Error(
                "Production account email delivery is not configured.",
                hint="Configure the SMTP credentials and enable ROLA_USE_SES.",
                id="rola.E001",
            )
        ]
    return []
