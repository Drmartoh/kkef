import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        self.group_name = f"notify_{user.pk}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):  # noqa: ARG002
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):  # noqa: ARG002
        await self.send(
            text_data=json.dumps({"detail": "Read-only realtime channel.", "heartbeat": True})
        )

    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event.get("envelope", {})))
