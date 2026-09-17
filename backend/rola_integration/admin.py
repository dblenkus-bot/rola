"""Expose host email templates alongside contest configuration."""

from django.contrib import admin

from rolca.core.admin import ContestAdmin
from rolca.core.models import Contest

from .models import ContestNotification


class ContestNotificationInline(admin.StackedInline):
    """Configure the optional confirmation template on its contest."""

    model = ContestNotification
    extra = 1
    max_num = 1


class RolaContestAdmin(ContestAdmin):
    """Extend contest administration with the host's email configuration."""

    inlines = [*ContestAdmin.inlines, ContestNotificationInline]


admin.site.unregister(Contest)
admin.site.register(Contest, RolaContestAdmin)
