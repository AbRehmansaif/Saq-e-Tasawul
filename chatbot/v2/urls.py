from django.urls import path
from .views import ChatAPIView, ChatHistoryAPIView, SessionCreateAPIView, quick_search

app_name = 'chatbot'

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('session/create/', SessionCreateAPIView.as_view(), name='create_session'),
    path('session/<str:session_id>/history/', ChatHistoryAPIView.as_view(), name='chat_history'),
    path('search/quick/', quick_search, name='quick_search'),
]