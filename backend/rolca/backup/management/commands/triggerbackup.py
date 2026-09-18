""".. Ignore pydocstyle D400.

======================
Command: triggerbackup
======================
"""

from django.core.management.base import BaseCommand

from rolca.backup.models import FileBackup
from rolca.backup.queue import enqueue_backup
from rolca.core.models import File


class Command(BaseCommand):
    """Start backup via signal by django channels."""

    help = "Start backup via signal by django channels."

    def handle(self, *args, **options):
        """Command handle."""
        # Create missing backup objects.
        FileBackup.objects.bulk_create(
            [FileBackup(source=file) for file in File.objects.filter(filebackup=None)]
        )

        enqueue_backup()
