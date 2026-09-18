"""Dispatch pending backups to the configured worker channel."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import ChannelFull, get_channel_layer

from rolca.backup.protocol import CHANNEL_BACKUP, TYPE_FILE

logger = logging.getLogger(__name__)


def enqueue_backup(file_backup_pk: int | None = None) -> None:
    """Request processing of one pending backup or all pending backups.

    Parameters
    ----------
    file_backup_pk : int or None, optional
        Backup record to process, or ``None`` to process all pending records.
    """
    message: dict[str, str | int] = {"type": TYPE_FILE}
    if file_backup_pk is not None:
        message["file_backup_pk"] = file_backup_pk
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.send)(CHANNEL_BACKUP, message)
    except ChannelFull:
        logger.warning("Cannot trigger backup because channel is full.")
