from rest_framework import serializers
from .models import Ticket, TicketMessage

class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['id', 'sender_id', 'sender_name', 'message', 'attachment', 'created_at']
        read_only_fields = ['id', 'sender_id', 'sender_name', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'user_id', 'user_name', 'subject', 'description', 'status', 'priority', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'user_id', 'user_name', 'status', 'created_at', 'updated_at']

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'priority']

class AdminTicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority']
