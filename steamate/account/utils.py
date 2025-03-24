import requests
from .models import User, Genre, Game, UserPreferredGame
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from rest_framework.response import Response
from django.db.utils import IntegrityError
from rest_framework import status
from django.db import transaction

load_dotenv()
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
logger = logging.getLogger(__name__)



def get_or_create_genre(genre_name):
    """
    장르 이름을 받아서 Genre 테이블에 저장하거나 가져오기
    """
    genre, created = Genre.objects.get_or_create(
        genre_name=genre_name.strip()
    )
    return genre

def get_or_create_game(appid):
    """
    Steam API에서 게임 정보를 가져와 Game 테이블에 저장하거나 가져오기
    """
    
    #  이미 게임이 존재하면 그대로 반환
    game = Game.objects.filter(appid=appid).first()
    if game:
        return game  # 기존 데이터 반환

    # Steam API에서 게임 정보 가져오기
    response = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    
    try:
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Steam API 오류 (appid={appid}): {e}")
        return None  # API 호출 실패 시 None 반환
    
    # API 응답 확인
    if not data.get(str(appid), {}).get("success", False):
        print(f"Steam API에서 게임 {appid} 정보를 찾을 수 없음.")
        return None  # API에 게임 정보가 없음
    
    game_data = data[str(appid)]["data"]  # 실제 게임 데이터 가져오기

    # 출시 날짜 변환 (없으면 None 저장)
    release_date = game_data.get("release_date", {}).get("date", None)
    try:
        released_at = datetime.strptime(release_date, "%Y-%m-%d").date() if release_date else None
    except ValueError:
        released_at = None  # 변환 실패 시 None 저장

    # 장르 저장 및 연결
    genre_names = []
    if "genres" in game_data:
        for genre in game_data["genres"]:
            genre_obj = get_or_create_genre(genre["description"])
            genre_names.append(genre_obj)  # 리스트에 추가

    # 게임 저장
    game = Game.objects.create(
        appid=appid,
        title=game_data.get("name"),
        genre=", ".join([g.genre_name for g in genre_names]),  # 장르 리스트 문자열로 저장
        released_at=released_at,
        description=game_data.get("short_description", ""),
        review_score=game_data.get("metacritic", {}).get("score", 0),
        header_image=game_data.get("header_image", ""),
        trailer_url=game_data.get("movies", [{}])[0].get("webm", {}).get("480", "") if "movies" in game_data else ""
    )

    return game  # 새로 저장된 게임 반환


def fetch_steam_library(steamid):
    """
    Steam에서 사용자의 보유 게임 목록을 가져옴
    appid, name, playtime_forever를 반환
    """
    API_KEY = STEAM_API_KEY  # Steam API Key
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    
    params = {
        'key': API_KEY,
        'steamid': steamid,
        'include_appinfo': 1,
        'include_played_free_games': 1,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Steam API 요청 실패 (status code: {response.status_code}) - 응답: {response.text}")
            return [], [], []
        
        data = response.json()
        
        if "response" not in data or "games" not in data["response"]:
            logger.warning(f"Steam API 응답 데이터 이상: {data}")
            return [], [], []
        
        
        games = data.get("response", {}).get("games", [])  # 게임 목록 반환
        
        if not games:
            logger.info(f"사용자의 Steam 라이브러리에 등록된 게임이 없음 (steam_id: {steamid})")
            return [], [], []
        
        game_data = []
        for game in games:
            appid = game.get("appid")
            name = game.get("name")
            playtime = game.get("playtime_forever", 0)
            
            if appid and name:
                game_data.append((appid, name, playtime))
        if game_data:
            game_appid, game_names, game_playtime = zip(*game_data)
            return list(game_appid), list(game_names), list(game_playtime)
        
    except Exception as e:
        logger.exception(f"Steam 라이브러리 가져오기 실패 (error: {str(e)}")
        return  [],[],[] # 에러 발생 시 빈 리스트 반환

