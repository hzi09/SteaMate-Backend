from django.urls import path
from .views import ChatSessionAPIView, ChatMessageAPIView


urlpatterns = [
    path('', ChatSessionAPIView.as_view()),
    path('<int:session_id>/', ChatSessionAPIView.as_view()),
    path('<int:session_id>/message/', ChatMessageAPIView.as_view()),
    path('<int:session_id>/message/<int:message_id>/', ChatMessageAPIView.as_view())
]