from django.urls import path
from . import views

urlpatterns = [
    path('start_convo/<int:user_id>/', views.start_convo, name='start_convo'),
    path('get_convo/<int:convo_id>/', views.get_conversation, name='get_conversation'),
    path('convos/', views.conversations, name='conversations'),
    path('mark_read/<int:convo_id>/', views.mark_read, name='mark_read'),
    path('message/<int:message_id>/', views.delete_message, name='delete_message')
]
