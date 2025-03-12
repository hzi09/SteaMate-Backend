from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer

from .utils import chatbot_call, bring_session_history, delete_messages_from_history

from django.shortcuts import get_object_or_404

# Create your views here.
class ChatSessionAPIView(APIView):

    # 인증되지 않은 유저가 접근하면 401에러를 반환
    permission_classes = [IsAuthenticated]

    # 유저 세션 목록 조회
    def get(self, request):
        sessions = ChatSession.objects.filter(user_id=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        
        return Response({"message" : "세션 목록 조회 완료", "data" : serializer.data}, status=status.HTTP_200_OK)
    
    # 세션 생성
    def post(self, request):
        serializer = ChatSessionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user_id = request.user)
            return Response({"message" : "세션 생성 완료", "data" : serializer.data}, status=status.HTTP_201_CREATED)
    
    # 세션 삭제
    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, pk=session_id)
        session.delete()
        return Response({"message" : "세션 삭제 완료"}, status=status.HTTP_200_OK)

class ChatMessageAPIView(APIView):

    # 인증되지 않은 유저가 접근하면 401에러를 반환
    permission_classes = [IsAuthenticated]

    # 세션 내역 조회
    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, pk=session_id)
        # RDB에 있는 대화 내역을 메모리에 저장하는 함수
        # 지금은 대화 내역을 불러오고 30분이 지나면 메모리에서 삭제 됨
        # 추후 대화 내역을 저장하고 30분이 지나도 메모리에 남아있도록 수정 필요(튜터님께 여쭤보기)
        bring_session_history(session_id)
        messages = session.chat_messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response({"message" : "대화 내역 조회 완료", "data" : serializer.data}, status=status.HTTP_200_OK)
    
    # 대화 내역 생성
    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, pk=session_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # 선호장르 가져오기
            genre = [genre.genre_name for genre in request.user.preferred_genre.all()]
            # 선호 게임 정보 가져오기
            preferred_games = request.user.preferred_game.all()
            appid = [ game.appid for game in preferred_games ]
            game = [ game.title for game in preferred_games ]
            # 챗봇 메시지 생성
            chatbot_message = chatbot_call(request.data["user_message"], session_id, genre=genre, game=game, appid=appid)
            serializer.save(session_id=session, chatbot_message=chatbot_message)
            return Response({"message" : "대화 내역 생성 완료", "data" : serializer.data}, status=status.HTTP_200_OK)
    
    # 대화 내역 삭제
    def delete(self, request, session_id, message_id):
        # DB에서 메시지 가져오기
        message = get_object_or_404(ChatMessage, pk=message_id)
        # 메모리 히스토리에서 메시지 삭제
        delete_messages_from_history(session_id, message.user_message)
        # DB에서 메시지 삭제
        message.delete()
        return Response({"message" : "메시지 삭제 완료"}, status=status.HTTP_200_OK)
    
    def put(self, request, session_id, message_id):
        # DB에서 메시지 가져오기
        message = get_object_or_404(ChatMessage, pk=message_id)
        # 세션 가져오기
        session = get_object_or_404(ChatSession, pk=session_id)
        # 메모리 히스토리에서 메시지 삭제
        if message.user_message:
            delete_messages_from_history(session_id, message.user_message)
        serializer = ChatMessageSerializer(message, data=request.data)
        if serializer.is_valid(raise_exception=True):
            # 선호장르 가져오기
            genre = [genre.genre_name for genre in request.user.preferred_genre.all()]
            # 선호 게임 정보 가져오기(appid, game_title)
            preferred_games = request.user.preferred_game.all()
            appid = [game.appid for game in preferred_games]
            game = [game.title for game in preferred_games]
            # 챗봇 메시지 생성
            chatbot_message = chatbot_call(request.data["user_message"], session_id, genre=genre, game=game, appid=appid)
            serializer.save(session_id=session, chatbot_message=chatbot_message)
            return Response({"message" : "메시지 수정 완료", "data" : serializer.data}, status=status.HTTP_200_OK)