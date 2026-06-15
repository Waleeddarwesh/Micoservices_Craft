from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.utils.translation import gettext as _
from rest_framework.filters import SearchFilter
from .models import Notification
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import create_notifications_for_all_suppliers,create_notifications_for_all_users
from rest_framework.decorators import action
from .models import NotificationPreference

class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['message']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).select_related('user')

    @action(detail=False, methods=['get', 'put', 'patch'])
    def preferences(self, request):
        prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(prefs)
            return Response(serializer.data)
        
        serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def send_to_suppliers_view(request):
    message = request.data.get('message', '')
    if not message:
        return Response(
            {'error': _('Message field is required.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    create_notifications_for_all_suppliers(message)
    
    return Response(
        {"status": _("Notifications have been created and sent to all suppliers.")},
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def send_to_all_users_view(request):
    """
    An admin-only endpoint to trigger sending notifications to all users.
    """
    message = request.data.get('message', '')
    if not message:
        return Response(
            {'error': _('Message field is required.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    create_notifications_for_all_users(message)
    
    return Response(
        {"status": _("Notifications have been created and sent to all users.")},
        status=status.HTTP_201_CREATED
    )