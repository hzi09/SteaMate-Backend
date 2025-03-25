import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(token):
    """
    JWT 토큰에서 사용자 정보를 추출하는 함수
    """
    try:
        # 토큰에서 payload 디코딩
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get('user_id')
        
        # 사용자 정보 조회
        user = User.objects.get(id=user_id)
        return user
    except (jwt.PyJWTError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    웹소켓 요청에 대한 JWT 인증을 처리하는 미들웨어
    """
    
    async def __call__(self, scope, receive, send):
        # 요청 헤더에서 토큰 추출
        headers = dict(scope['headers'])
        
        # 쿼리 파라미터에서 토큰 추출 시도
        query_params = parse_qs(scope.get('query_string', b'').decode())
        
        token = None
        if 'token' in query_params:
            token = query_params['token'][0]
        
        # 헤더에서 Authorization 토큰 확인
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        # 토큰이 없으면 쿼리 파라미터에서 확인
        if not token and 'token' in query_params:
            token = query_params['token']
        
        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send) 