import django.db.models.deletion
import rolca.core.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('dob', models.DateField(blank=True, null=True)),
                ('school', models.CharField(blank=True, max_length=100, null=True)),
                ('mentor', models.CharField(blank=True, max_length=100, null=True)),
                ('club', models.CharField(blank=True, max_length=100, null=True)),
                ('distinction', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'author',
                'verbose_name_plural': 'authors',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateTimeField(verbose_name='Start date')),
                ('end_date', models.DateTimeField(verbose_name='End date')),
                ('publish_date', models.DateTimeField(blank=True, verbose_name='Publish date')),
                ('login_required', models.BooleanField(default=False, verbose_name='Login required')),
                ('header_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('notice_html', models.TextField(default='')),
                ('confirmation_html', models.TextField(default='')),
                ('dob_required', models.BooleanField(default=False)),
                ('club_show', models.BooleanField(default=False)),
                ('club_required', models.BooleanField(default=False)),
                ('school_show', models.BooleanField(default=False)),
                ('school_required', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'contest',
                'verbose_name_plural': 'contests',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.author')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'submission',
                'verbose_name_plural': 'submissions',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('file', models.ImageField(upload_to=rolca.core.models.generate_file_filename, validators=[rolca.core.models.validate_image])),
                ('thumbnail', models.ImageField(upload_to=rolca.core.models.generate_thumb_filename)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('submission', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='core.submission')),
            ],
            options={
                'verbose_name': 'file',
                'verbose_name_plural': 'files',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.author')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_sets', to='core.contest')),
                ('submissions', models.ManyToManyField(to='core.submission')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'submission set',
                'verbose_name_plural': 'submission sets',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('is_series', models.BooleanField(default=False)),
                ('n_photos', models.IntegerField(verbose_name='Number of photos')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='core.contest')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'theme',
                'verbose_name_plural': 'themes',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.theme'),
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('kind', models.SmallIntegerField(choices=[(1, 'School')])),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('kind', 'name'), name='unique_name_kind')],
            },
        ),
    ]
