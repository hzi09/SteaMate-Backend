import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatMessageSerializer
from .utils_v5 import get_chatbot_message
from .history import delete_session_history, delete_messages_from_history

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
        
        # 사용자 정보 가져오기
        self.tags = await database_sync_to_async(lambda: [tags.tag.name for tags in self.user.preferred_tags.all()])()
        library_games = await database_sync_to_async(lambda: self.user.library_games.all())()
        self.appid = await database_sync_to_async(lambda: [games.game.appid for games in library_games])()
        self.game = await database_sync_to_async(lambda: [games.game.title + ' (' + '플레이 시간: ' + str(games.playtime) + '분)' + ' ('+ 'appid: ' + str(games.game.appid) + ')' for games in library_games.order_by('-playtime')])()
        self.preferred_games = await database_sync_to_async(lambda: [preferred_games.game.title + ' ('+ 'appid: ' + str(preferred_games.game.appid) + ')' for preferred_games in self.user.preferred_games.all()])()
        
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
            
        # 메시지 수정 처리
        if data.get('type') == 'message_modify':
            await self.message_modify(text_data)
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
                if serializer.is_valid(raise_exception=True):
                    # 스트리밍 응답 처리
                    aggregated_response = ""
                    async for chunk in get_chatbot_message(user_message, self.session_id, self.tags, self.game, self.appid, self.preferred_games):
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
        
    async def message_modify(self, text_data):
        """메시지 수정 시 호출되는 메서드"""
        data = json.loads(text_data)
        message_id = data['message_id']
        new_message = data['new_message']
        
        try:
            # 처리 시작 알림
            await self.send(text_data=json.dumps({
                'status': 'processing',
                'message': '메시지 수정 중입니다.'
            }))
            
            # DB에서 메시지 가져오기
            message = await database_sync_to_async(get_object_or_404)(ChatMessage, pk=message_id)
            
            # 이전 메시지 히스토리에서 삭제
            if message.user_message:
                await database_sync_to_async(delete_messages_from_history)(self.session_id, message.user_message)
            
            # 메시지 유효성 검사
            serializer = ChatMessageSerializer(message, data={'user_message': new_message})
            if serializer.is_valid(raise_exception=True):
                # 새로운 챗봇 응답 생성 및 스트리밍
                aggregated_response = ""
                async for chunk in get_chatbot_message(new_message, self.session_id, self.tags, self.game, self.appid, self.preferred_games):
                    aggregated_response += chunk
                    await self.send(text_data=json.dumps({
                        'response': aggregated_response,
                        'is_streaming': True
                    }))
                
                # 최종 응답 전송
                await self.send(text_data=json.dumps({
                    'response': aggregated_response,
                    'is_streaming': False
                }))
                
                # DB 업데이트
                await database_sync_to_async(serializer.save)(
                    session_id=self.session,
                    chatbot_message=aggregated_response
                )
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': f'메시지 수정 중 오류가 발생했습니다: {str(e)}'
            }))
    
    async def disconnect(self, close_code):
        """웹소켓 연결 종료 시 호출되는 메서드"""
        try:
            # 세션 내역 메모리에서 삭제 코드가 필요한 경우 여기에 작성
            await database_sync_to_async(delete_session_history)(self.session_id)
        except Exception as e:
            print(f"세션 내역 삭제 중 오류가 발생했습니다: {str(e)}")
    
    