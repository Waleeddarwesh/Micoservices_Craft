from django.db.models import Prefetch, Q, Max
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.translation import gettext as _

from accounts.models import User
from .models import Conversation, Message
from .serializers import ConversationListSerializer, ConversationSerializer
from .tasks import send_chat_notification_task


@api_view(['POST'])
def start_convo(request, user_id):
    participant = get_object_or_404(User, id=user_id)
    sender = request.user

    if request.user == participant:
        return Response(
            {'message': _('You cannot start a conversation with yourself.')},
            status=status.HTTP_400_BAD_REQUEST
        )

    conversation = Conversation.objects.get_or_create_personal_convo(request.user, participant)

    # ✨ Offload notification to Celery
    message = _("{user_name} started a conversation with you.").format(user_name=request.user.get_full_name)
    send_chat_notification_task.delay(
        sender.id, participant.id, message, conversation.id
    )

    serializer = ConversationSerializer(instance=conversation, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_conversation(request, convo_id):
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 50))
    except ValueError:
        offset, limit = 0, 50

    conversation = get_object_or_404(
        Conversation.objects.prefetch_related(
            Prefetch('messages', queryset=Message.objects.order_by('-timestamp')[offset:offset+limit])
        ),
        id=convo_id
    )

    if request.user not in [conversation.initiator, conversation.receiver]:
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer = ConversationSerializer(instance=conversation, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def conversations(request):
    conversation_list = Conversation.objects.filter(
        Q(initiator=request.user) | Q(receiver=request.user)
    ).annotate(
        last_msg_time=Max('messages__timestamp')
    ).prefetch_related(
        Prefetch('messages', queryset=Message.objects.order_by('-timestamp')[:1])
    ).select_related('initiator', 'receiver').order_by('-last_msg_time')

    serializer = ConversationListSerializer(instance=conversation_list, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
def mark_read(request, convo_id):
    conversation = get_object_or_404(Conversation, id=convo_id)
    if request.user not in [conversation.initiator, conversation.receiver]:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # Mark messages sent by the OTHER person as read
    Message.objects.filter(
        conversation=conversation
    ).exclude(sender=request.user).update(is_read=True)
    
    return Response({'status': _('messages marked as read')}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user != message.sender:
        return Response({'error': _('You can only delete your own messages.')}, status=status.HTTP_403_FORBIDDEN)
    
    # Soft delete
    message.is_deleted = True
    message.save()
    
    return Response({'status': _('message deleted')}, status=status.HTTP_200_OK)