from rest_framework import serializers
from .models import ChatMessage, ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):

    # class Meta 오버라이딩
    class Meta:
        # 직렬화할 데이터의 기반이 되는 모델 설정
        model = ChatSession
        # 직렬화 대상 필드 지정
        fields = "__all__"
        # 읽기 전용 필드 지정
        read_only_fields = [
            "user_id",
        ]



class ChatMessageSerializer(serializers.ModelSerializer):

    # class Meta 오버라이딩
    class Meta:
        # 직렬화할 데이터의 기반이 되는 모델 설정
        model = ChatMessage
        # 직렬화 대상 필드 지정
        fields = "__all__"
        # 읽기 전용 필드 지정
        read_only_fields = [
            "chatbot_message",
            "session_id",
        ]