from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"].get("chat_id")
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"[Disconnected] chat_id: {self.chat_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        file = data.get('file')
        filename = data.get("filename")
        content_type = data.get("content_type", "application/octet-stream")
        chat_id = data.get("chat_id", self.chat_id)
        sender_id = data.get("sender_id", self.scope["user"].id)
        from chat.tasks import upload_file_to_gridfs
        import base64
        from .models import Message
        # message_id = str(uuid.uuid4())
        if file:
            file_data = base64.b64decode(file)
            message_id = str(uuid.uuid4())
            upload_file_to_gridfs.delay(
                file_data_str=file_data,
                filename=filename,
                content_type=content_type,
                chat_id=chat_id,
                sender_id=sender_id,
                message_id=message_id
            )
            msg_data = {
                "_id": message_id,
                "chat_id": self.chat_id,
                "sender_id": int(sender_id),
                "timestamp": datetime.utcnow()
            }
            print(f"[Message Data] {msg_data}")

            if message:
                msg_data["text"] = message

            Message().insert_one(msg_data)


        if message and len(message) > 0:
            msg_data = {
                "_id": str(uuid.uuid4()),
                "chat_id": self.chat_id,
                "sender_id": int(sender_id),
                "timestamp": datetime.utcnow()
            }
            print(f"[Message Data] {msg_data}")

            if message:
                msg_data["text"] = message

            Message().insert_one(msg_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": sender_id
                }
            )

    async def chat_message(self, event):
        print(f"[Chat Message] Group: {self.room_group_name}, {event} ")
        await self.send(text_data=json.dumps({
            "message": event.get("message", ""),
            "sender_id": event.get("sender_id"),
            "file_url": event.get("file_url", None),  # ✅ include this
            "file_type": event.get("file_type", None),  # ✅ include this
            "file_id": event.get("file_id", None),
        }))
