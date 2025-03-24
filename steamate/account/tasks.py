from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from .models import UserPreferredGame, User
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
    Celery Task: 사용자의 Steam 라이브러리를 가져와 UserPreferredGame에 저장
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
    
    user_preferred_games = []
    user_preferred_genres = set()
    
    for i in range(len(appids)):
        game = get_or_create_game(appid=appids[i])
        if game:
            user_preferred_games.append(UserPreferredGame(user=user, game=game, playtime=playtimes[i]))
            
            genre_names = [g.strip() for g in game.genre.split(",") if g.strip()]
            for genre_name in genre_names:
                genre_instance = get_or_create_genre(genre_name)
                user_preferred_genres.add(genre_instance)
        else:
            logger.warning(f"게임 정보를 가져오지 못함 (appid: {appids[i]})")
            continue
    try:
        with transaction.atomic():
            if user_preferred_games:
                UserPreferredGame.objects.bulk_create(user_preferred_games)
            if user_preferred_genres:
                user.preferred_genre.add(*user_preferred_genres)
    except IntegrityError as e:
        logger.error(f"UserPreferredGame 생성 오류: {str(e)}")
        return {"status": "error", "message": "게임 데이터 저장 중 오류 발생"}
    
    return {"status":"success", "message":"라이브러리 저장 완료"}  # 정상 처리 시 None 반환