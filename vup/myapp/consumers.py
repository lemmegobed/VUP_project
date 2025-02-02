import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Chat_Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.utils.timezone import now

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f"chat_{self.chat_room_id}"

        # เข้าร่วมห้องแชท
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']

        chat_message = await self.save_message(sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': chat_message.message,
                'sender': chat_message.sender.username,
                'created_at': chat_message.created_at.strftime("%H:%M, %d %b %Y"),
                'sender_profile': chat_message.sender.profile.url,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, message):
        chat_room = ChatRoom.objects.get(id=self.chat_room_id)
        return Chat_Message.objects.create(chatroom=chat_room, sender=sender, message=message, created_at=now())


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = f"notifications_{self.scope['user'].id}"  
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def send_notification(self, event):
#         """ส่งข้อมูลแจ้งเตือนทั้งหมดไปที่ WebSocket"""
#         await self.send(text_data=event["message"])  # ✅ ส่ง JSON ไปที่ Client

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         """เชื่อมต่อ WebSocket และเข้ากลุ่ม notifications"""
#         await self.channel_layer.group_add("notifications", self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         """ตัดการเชื่อมต่อ WebSocket"""
#         await self.channel_layer.group_discard("notifications", self.channel_name)

#     async def receive(self, text_data):
#         """รับข้อความจาก WebSocket (ถ้ามี)"""
#         data = json.loads(text_data)
#         message = data["message"]
#         await self.send(text_data=json.dumps({"message": message}))

#     async def send_notification(self, event):
#         """ส่งแจ้งเตือนไปยัง Client"""
#         message = event["message"]
#         await self.send(text_data=json.dumps({"message": message}))