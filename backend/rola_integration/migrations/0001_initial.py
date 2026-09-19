import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('drf_user', '0001_initial'),
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
    ]
