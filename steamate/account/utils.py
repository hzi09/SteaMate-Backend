import requests
from .models import User, Genre, Game, UserPreferredGame, Tag, GameTag
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from rest_framework.response import Response
from django.db.utils import IntegrityError
from rest_framework import status
from django.db import transaction
from bs4 import BeautifulSoup

load_dotenv()
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
logger = logging.getLogger(__name__)

def get_steam_tags(appid):
    """
    Steam 스토어 페이지에서 태그 정보를 크롤링하여 리스트로 반환
    """
    url = f"https://store.steampowered.com/app/{appid}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"[태그 크롤링 실패] appid={appid}, error={e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    tag_elements = soup.select(".glance_tags.popular_tags a")

    tags = [tag.get_text(strip=True) for tag in tag_elements]
    return tags


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
    )
    
    # 태그 크롤링 및 저장
    tag_list = get_steam_tags(appid)
    for tag in tag_list:
        tag_obj, _ = Tag.objects.get_or_create(name=tag)
        GameTag.objects.get_or_create(game=game, tag=tag_obj)

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