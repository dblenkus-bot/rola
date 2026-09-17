"""Exercise image processing, historical migrations, and backup delivery."""

import os
import uuid
from unittest.mock import patch

import pytest
from asgiref.sync import async_to_sync
from botocore.exceptions import ClientError
from channels.exceptions import ChannelFull
from channels.layers import get_channel_layer
from django.core.management import call_command
from django.test import override_settings
from PIL import Image

from rolca.backup.consumers import BackupConsumer
from rolca.backup.models import FileBackup
from rolca.backup.protocol import CHANNEL_BACKUP, TYPE_FILE
from rolca.backup.signals import commit_signal
from tests.factories import create_user
from tests.test_workflows import photo

pytestmark = pytest.mark.django_db


def test_upload_creates_jpeg_thumbnail_and_pending_backup():
    user = create_user("photographer")
    image = photo(user)
    with image.thumbnail.open("rb") as source, Image.open(source) as thumb:
        assert thumb.size == (400, 300)
        assert thumb.format == "JPEG"
    assert FileBackup.objects.get(source=image).done is None


def test_backup_only_enqueues_after_commit(django_capture_on_commit_callbacks):
    user = create_user("photographer")
    with patch("rolca.backup.signals.commit_signal") as enqueue:
        with django_capture_on_commit_callbacks(execute=True):
            image = photo(user)
            enqueue.assert_not_called()
        enqueue.assert_called_once_with(FileBackup.objects.get(source=image).pk)


def test_backup_queue_full_leaves_pending_record(caplog):
    image = photo(create_user("photographer"))
    backup = FileBackup.objects.get(source=image)
    with patch("rolca.backup.signals.async_to_sync") as sync:
        sync.return_value.side_effect = ChannelFull
        commit_signal(backup.pk)
    assert "channel is full" in caplog.text
    backup.refresh_from_db()
    assert backup.done is None


def test_backup_failure_remains_retryable_then_completes():
    image = photo(create_user("photographer"))
    backup = FileBackup.objects.get(source=image)
    message = {"file_backup_pk": backup.pk}
    with patch("rolca.backup.consumers.boto3.Session") as session:
        client = session.return_value.client.return_value
        client.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "Unavailable", "Message": "Retry"}}, "PutObject"
        )
        BackupConsumer().backup_file(message)
        backup.refresh_from_db()
        assert backup.done is None
        client.upload_fileobj.side_effect = None
        BackupConsumer().backup_file(message)
        backup.refresh_from_db()
        assert backup.done is not None
        BackupConsumer().backup_file(message)
        assert client.upload_fileobj.call_count == 2


def test_triggerbackup_reconciles_missing_backup_records():
    image = photo(create_user("photographer"))
    FileBackup.objects.all().delete()
    with patch("rolca.backup.management.commands.triggerbackup.async_to_sync") as sync:
        call_command("triggerbackup")
        call_command("triggerbackup")
        assert FileBackup.objects.filter(source=image).count() == 1
        assert sync.return_value.call_args.args == (CHANNEL_BACKUP, {"type": TYPE_FILE})


@pytest.mark.redis
@pytest.mark.django_db(transaction=True)
def test_redis_message_is_processed_by_configured_asgi_worker():
    url = os.environ.get("ROLCA_REDIS_URL")
    if not url:
        pytest.skip("Set ROLCA_REDIS_URL to run the Redis worker integration test.")
    from tests.routing import application

    # A unique prefix keeps this test independent of other queues on the server.
    layer_settings = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [url], "prefix": f"rolca-test-{uuid.uuid4().hex}"},
        }
    }
    with (
        override_settings(CHANNEL_LAYERS=layer_settings),
        patch("rolca.backup.consumers.boto3.Session") as session,
    ):
        user = create_user("photographer")
        image = photo(user)
        backup = FileBackup.objects.get(source=image)
        layer = get_channel_layer()

        async def run_worker():
            import asyncio

            from asgiref.testing import ApplicationCommunicator

            message = await asyncio.wait_for(layer.receive(CHANNEL_BACKUP), timeout=5)
            assert message["file_backup_pk"] == backup.pk
            worker = ApplicationCommunicator(
                application, {"type": "channel", "channel": CHANNEL_BACKUP}
            )
            await worker.send_input(message)
            try:
                for _ in range(100):
                    if await FileBackup.objects.filter(
                        pk=backup.pk, done__isnull=False
                    ).aexists():
                        return
                    if worker.future.done():
                        worker.future.result()
                    await asyncio.sleep(0.02)
                pytest.fail("Backup worker did not mark the upload complete.")
            finally:
                await worker.wait(timeout=0.1)
                await layer.flush()
                await layer.close_pools()

        async_to_sync(run_worker)()
        backup.refresh_from_db()
        assert backup.done is not None
        session.return_value.client.return_value.upload_fileobj.assert_called_once()
