from rest_framework import serializers
from .models import Chat_Message

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_Message
        fields = ['id', 'chatroom', 'sender', 'message', 'created_at']
