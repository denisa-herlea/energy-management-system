from rest_framework import serializers
from .models import Thread, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ThreadSerializer(serializers.ModelSerializer):
    chatmessage_thread = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = '__all__'
