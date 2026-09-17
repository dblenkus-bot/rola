"""Remove the historical email relation only after verifying its replacement."""

from django.db import migrations
from django.db.models import F


def verify_confirmation_templates(apps, schema_editor):
    """Verify all template links before dropping the legacy column."""
    Contest = apps.get_model("core", "Contest")
    Notification = apps.get_model("rola_integration", "ContestNotification")
    database = schema_editor.connection.alias
    contests = Contest.objects.using(database).exclude(confirmation_email_id=None)
    notifications = Notification.objects.using(database).exclude(confirmation_email_id=None)
    if contests.count() != notifications.count() or contests.exclude(
        confirmation_email_id=F("notification__confirmation_email_id")
    ).exists():
        raise RuntimeError("Contest confirmation templates were not copied exactly.")


def restore_confirmation_templates(apps, schema_editor):
    """Restore template associations when reversing the column removal."""
    Contest = apps.get_model("core", "Contest")
    Notification = apps.get_model("rola_integration", "ContestNotification")
    database = schema_editor.connection.alias
    for configuration in Notification.objects.using(database).iterator():
        Contest.objects.using(database).filter(pk=configuration.contest_id).update(
            confirmation_email_id=configuration.confirmation_email_id
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_auto_20210208_1803"),
        ("rola_integration", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(verify_confirmation_templates, restore_confirmation_templates),
        migrations.RemoveField(model_name="contest", name="confirmation_email"),
    ]
