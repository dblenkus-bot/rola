""".. Ignore pydocstyle D400.

===============
Signal Handlers
===============

"""

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from rolca.backup.models import FileBackup
from rolca.backup.queue import enqueue_backup as commit_signal
from rolca.core.models import File


@receiver(post_save, sender=File)
def backup_post_save_handler(sender, instance, created, **kwargs):
    """Trigger a backup after a new File is created."""
    if created:
        file_backup = FileBackup.objects.create(source=instance)
        transaction.on_commit(lambda: commit_signal(file_backup.pk))
