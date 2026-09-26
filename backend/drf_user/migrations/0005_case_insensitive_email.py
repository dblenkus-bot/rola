import django.db.models.functions.text
from django.db import migrations, models
from django.db.models.functions import Lower


def normalize_emails(apps, schema_editor):
    """Reject case-only duplicates before normalizing stored addresses."""
    users = apps.get_model("drf_user", "User").objects.using(
        schema_editor.connection.alias
    )
    duplicates = (
        users.order_by()
        .values(normalized_email=Lower("email"))
        .annotate(count=models.Count("pk"))
        .filter(count__gt=1)
    )
    if duplicates.exists():
        raise RuntimeError(
            "Case-insensitive duplicate user email addresses exist. "
            "Resolve them manually, then rerun the migration."
        )
    users.update(email=Lower("email"))


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("drf_user", "0004_email"),
    ]

    operations = [
        migrations.RunPython(normalize_emails, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("email"),
                name="drf_user_email_ci_unique",
            ),
        ),
    ]
