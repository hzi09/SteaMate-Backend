import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatMessageSerializer
from .utils_v5 import bring_session_history, delete_messages_from_history, get_chatbot_message
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_session_and_user(session_id):
    session = get_object_or_404(ChatSession, pk=session_id)
    return session, session.user_id

class ChatConsumer(AsyncWebsocketConsumer):
    """
    웹소켓 연결을 처리하는 소비자 클래스
    """
    async def connect(self):
        """웹소켓 연결 시 호출되는 메서드"""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session, session_user = await get_session_and_user(self.session_id)
        self.user = self.scope['user']
        
        # 권한 확인 - 세션 소유자만 접근 가능
        if self.user.is_anonymous or session_user.id != self.user.id:
            await self.close(code=4003)
            return
        
        # 웹소켓 연결 수락
        await self.accept()
        
        # 연결 확인 메시지 전송
        await self.send(text_data=json.dumps({
            'status': 'connected',
            'message': '웹소켓 연결이 설정되었습니다.'
        }))
    
    async def receive(self, text_data):
        """웹소켓 메시지 수신 시 호출되는 메서드"""
        data = json.loads(text_data)
        
        # ping 메시지 처리
        if data.get('type') == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'message': 'Connection is alive!'
            }))
            return
            
        # 일반 메시지 처리
        if 'message' in data:
            user_message = data['message']
            
            # 처리 시작 알림
            await self.send(text_data=json.dumps({
                'status': 'processing',
                'message': '메시지 처리 중입니다.'
            }))
            
            try:
                # 메시지 유효성 검사
                serializer = ChatMessageSerializer(data={'user_message': user_message})
                await database_sync_to_async(serializer.is_valid)(raise_exception=True)
                
                # 세션 정보 가져오기
                genre = await database_sync_to_async(lambda: [genre.genre_name for genre in self.user.preferred_genre.all()])()
                # 선호 게임 정보 가져오기(appid, game_title)
                preferred_games = await database_sync_to_async(lambda: self.user.preferred_game.all())()
                appid = await database_sync_to_async(lambda: [game.appid for game in preferred_games])()
                game = await database_sync_to_async(lambda: [game.title for game in preferred_games])()
                
                # 스트리밍 응답 처리
                aggregated_response = ""
                async for chunk in get_chatbot_message(user_message, self.session_id, genre, game, appid):
                    aggregated_response += chunk
                    # 각 청크마다 스트리밍 응답 전송
                    await self.send(text_data=json.dumps({
                        'response': aggregated_response,
                        'is_streaming': True
                    }))
                
                # 최종 응답 전송 및 DB 저장
                await self.send(text_data=json.dumps({
                    'response': aggregated_response,
                    'is_streaming': False
                }))
                
                # DB에 메시지 저장
                await database_sync_to_async(serializer.save)(
                    session_id=self.session,
                    chatbot_message=aggregated_response
                )
                
            except Exception as e:
                # 오류 처리
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': f'메시지 처리 중 오류가 발생했습니다: {str(e)}'
                }))
    
    async def disconnect(self, close_code):
        """웹소켓 연결 종료 시 호출되는 메서드"""
        # 세션 내역 메모리에서 삭제 코드가 필요한 경우 여기에 작성
        pass
    
    