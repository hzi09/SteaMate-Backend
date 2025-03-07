from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

from .utils import chatbot_call


# Create your views here.
class ChatSessionAPIView(APIView):

    # 인증되지 않은 유저가 접근하면 401에러를 반환
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.all()
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ChatSessionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user_id = request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ChatMessageAPIView(APIView):

    # 인증되지 않은 유저가 접근하면 401에러를 반환
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = ChatSession.objects.get(pk=session_id)
        messages = session.chat_messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, session_id):
        session = ChatSession.objects.get(pk=session_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            chatbot_message = chatbot_call(request.data["user_message"], session_id)
            serializer.save(session_id=session, chatbot_message=chatbot_message)
            return Response(serializer.data, status=status.HTTP_200_OK)
