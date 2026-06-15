import base64
import json
import secrets

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile

from accounts.models import User
from .tasks import send_chat_notification_task
from .models import Conversation, Message
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        await self.update_user_presence(is_online=True)
        # Broadcast presence
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "user_id": self.user.id,
                "is_online": True
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.update_user_presence(is_online=False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "is_online": False
                }
            )
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get("action", "message")
        
        if action == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "user_id": self.user.id,
                    "is_typing": data.get("is_typing", False)
                }
            )
        elif action == "read":
            message_id = data.get("message_id")
            if message_id:
                await self.mark_message_read(message_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "read_receipt",
                        "user_id": self.user.id,
                        "message_id": message_id
                    }
                )
        else:
            message_data = await self.create_message(
                text=data.get("message", ""),
                attachment_data=data.get("attachment"),
                reply_to_id=data.get("reply_to")
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_data": message_data
                },
            )

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            "action": "read",
            "user_id": event["user_id"],
            "message_id": event["message_id"]
        }))

    @database_sync_to_async
    def mark_message_read(self, message_id):
        Message.objects.filter(id=message_id).exclude(sender=self.user).update(is_read=True)

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            "action": "typing",
            "user_id": event["user_id"],
            "is_typing": event["is_typing"]
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "action": "status",
            "user_id": event["user_id"],
            "is_online": event["is_online"]
        }))

    async def chat_message(self, event):
        message_data = event["message_data"]
        # Wrap message in action to match other events
        await self.send(text_data=json.dumps({
            "action": "message",
            "data": message_data
        }))

    @database_sync_to_async
    def create_message(self, text, attachment_data=None, reply_to_id=None):
        conversation = Conversation.objects.select_related('initiator', 'receiver').get(id=int(self.room_name))
        message_attachment = None

        if attachment_data:
            try:
                file_str, file_ext = attachment_data["data"], attachment_data["format"]
                file_data = ContentFile(
                    base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
                )
                message_attachment = file_data
            except Exception as e:
                print(f"Error handling attachment: {e}")

        reply_msg = None
        if reply_to_id:
            reply_msg = Message.objects.filter(id=reply_to_id, conversation=conversation).first()

        message = Message.objects.create(
            sender=self.user,
            text=text,
            attachment=message_attachment,
            conversation=conversation,
            reply_to=reply_msg
        )

        recipient = (
            conversation.receiver
            if conversation.initiator == self.user
            else conversation.initiator
        )
        
        # ✨ Offload notification to Celery
        notification_message = f"You have a new message from {self.user.get_full_name}."
        send_chat_notification_task.delay(
            self.user.id, recipient.id, notification_message, conversation.id
        )
        
        return MessageSerializer(instance=message).data

    @database_sync_to_async
    def update_user_presence(self, is_online):
        from .models import UserPresence
        presence, _ = UserPresence.objects.get_or_create(user=self.user)
        presence.is_online = is_online
        presence.save()