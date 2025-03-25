from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from .models import UserPreferredGame, User, UserLibraryGame
from .utils import get_or_create_game, get_or_create_genre, fetch_steam_library
from django.db import transaction, IntegrityError
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_verification_email(subject, text_content, html_content, to_email):
    email = EmailMultiAlternatives(subject, text_content, None, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task
def fetch_and_save_user_games(user_id):
    """
    Celery Task: 사용자의 Steam 라이브러리를 가져와 UserLibraryGame에 저장
    """
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User does not exist (user_id: {user_id})")
        return {"status":"error", "message": "사용자가 존재하지 않습니다."}
    
    logger.info(f"Steam 라이브러리 가져오기 요청 시작 (Steam id : {user.steam_id})")
    
    appids, titles, playtimes = fetch_steam_library(user.steam_id)
    
    if not appids:
        logger.warning(f"Steam 라이브러리 불러오기 실패 또는 빈 데이터 (steam_id: {user.steam_id})")
        return {"status": "error", "message": "Steam 라이브러리가 비어있거나, 프로필이 비공개 상태입니다. Steam 설정에서 프로필과 게임 라이브러리를 공개로 변경해주세요."}
    
    try:
        with transaction.atomic():
            current_game_ids = []
        
            for i in range(len(appids)):
                game = get_or_create_game(appid=appids[i])
                if not game:
                    logger.warning(f"게임 정보를 가져오지 못함 (appid: {appids[i]})")
                    continue
            
                UserLibraryGame.objects.update_or_create(
                    user=user,
                    game=game,
                    defaults={"playtime": playtimes[i]}
                )

                current_game_ids.append(game.appid)
        
        # 사용자의 라이브러리에 없는 게임 삭제
        UserLibraryGame.objects.filter(user=user).exclude(game_appid__in=current_game_ids).delete()
                
    except IntegrityError as e:
        logger.error(f"UserLibraryGame 생성 오류: {str(e)}")
        return {"status": "error", "message": "게임 데이터 저장 중 오류 발생"}
    
    return {"status":"success", "message":"라이브러리 저장 완료"}
