from django.urls import re_path
from . import consumers

# 웹소켓 URL 패턴을 정의합니다
websocket_urlpatterns = [
    # 채팅관련 웹소켓 연결
    re_path(r'ws/chat/(?P<session_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]