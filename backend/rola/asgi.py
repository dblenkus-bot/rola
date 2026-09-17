"""Serve Django HTTP requests and optional backup worker messages."""

import os

from channels.routing import ChannelNameRouter, ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rola.settings")
django_application = get_asgi_application()

from django.conf import settings  # noqa: E402

protocols = {"http": django_application}
if settings.ROLA_BACKUP_ENABLED:
    from rolca.backup.consumers import BackupConsumer
    from rolca.backup.protocol import CHANNEL_BACKUP

    protocols["channel"] = ChannelNameRouter({CHANNEL_BACKUP: BackupConsumer.as_asgi()})

application = ProtocolTypeRouter(protocols)
