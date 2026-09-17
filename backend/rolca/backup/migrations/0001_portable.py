import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_portable'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileBackup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.DateTimeField(blank=True, null=True)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.file')),
            ],
        ),
    ]
