import django.db.models.deletion
from django.db import migrations, models
from itertools import batched


def copy_confirmation_templates(apps, schema_editor):
    """Copy existing contest-template links into the host-owned table."""
    Contest = apps.get_model("core", "Contest")
    Notification = apps.get_model("rola_integration", "ContestNotification")
    database = schema_editor.connection.alias
    links = Contest.objects.using(database).exclude(confirmation_email_id=None).values_list(
        "pk", "confirmation_email_id"
    )
    for batch in batched(links.iterator(), 500):
        Notification.objects.using(database).bulk_create([
            Notification(contest_id=contest, confirmation_email_id=template)
            for contest, template in batch
        ])


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0021_auto_20210208_1803'),
        ('drf_user', '0004_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmation_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drf_user.email')),
                ('contest', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification', to='core.contest')),
            ],
        ),
        migrations.RunPython(copy_confirmation_templates, migrations.RunPython.noop),
    ]
