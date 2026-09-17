"""Host-owned contest notification configuration."""

from django.db import models


class ContestNotification(models.Model):
    """Associate a contest with Rola's confirmation email template."""

    contest = models.OneToOneField(
        "core.Contest", on_delete=models.CASCADE, related_name="notification"
    )
    confirmation_email = models.ForeignKey(
        "drf_user.Email", null=True, blank=True, on_delete=models.SET_NULL
    )
