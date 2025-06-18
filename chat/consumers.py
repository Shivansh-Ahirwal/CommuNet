from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"].get("chat_id")
        self.room_group_name = f'chat_{self.chat_id}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"[Connected] chat_id: {self.chat_id}, channel: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"[Disconnected] chat_id: {self.chat_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')

        # Save to MongoDB
        from .models import Message
        Message().insert_one({
            "_id": str(uuid.uuid4()),
            "chat_id": self.chat_id,
            "sender_id": int(sender_id),
            "text": message,
            "timestamp": datetime.utcnow()
        })

        # Send message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))
