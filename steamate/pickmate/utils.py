from django.db import connection
import pandas as pd
import random
import re

def get_top_played_games(user_id, limit=10):
    """
    사용자가 가장 많이 플레이한 게임 ID 목록을 반환
    게임이 없을 경우, 랜덤으로 게임을 추천
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT game_id
            FROM account_userlibrarygame
            WHERE user_id = %s
            ORDER BY playtime DESC
            LIMIT %s
        """, [user_id, limit])
        
        rows = cursor.fetchall()
        
    if not rows:
        # 게임이 없으면 랜덤으로 전체 게임 목록에서 추천
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT appid
                FROM account_game  -- 게임 목록이 저장된 테이블
                ORDER BY RANDOM()
                LIMIT %s
            """, [limit])
            
            rows = cursor.fetchall()

    # 게임이 있으면 해당 게임들 반환, 게임이 없으면 랜덤 추천
    return [row[0] for row in rows]

def get_combined_similar_games(user_id, top_n=10, limit_per_game=10):
    """
    사용자가 가장 많이 플레이한 TOP 10 게임을 기준으로 `pgvector`에서 유사한 게임을 검색하고 결합
    """
    top_games = get_top_played_games(user_id, top_n)  # 사용자가 가장 많이 플레이한 10개 게임 조회
    combined_recommendations = {}

    for game_id in top_games:
        query = """
        SELECT cmetadata->>'appid' AS appid, embedding <=> (
            SELECT embedding FROM langchain_pg_embedding WHERE cmetadata->>'appid' = %s LIMIT 1
        ) AS similarity
        FROM langchain_pg_embedding
        ORDER BY similarity
        LIMIT %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, [str(game_id), limit_per_game])  # JSONB 값 비교를 위해 문자열 변환
            results = cursor.fetchall()

        for row in results:
            appid = row[0]
            similarity = row[1] if row[1] is not None else 0  # None 값을 0으로 대체
            
            if appid in combined_recommendations:
                combined_recommendations[appid] += similarity  # 유사도 점수 누적
            else:
                combined_recommendations[appid] = similarity

    # 유사도가 높은 순으로 정렬 후 반환
    sorted_recommendations = sorted(combined_recommendations.items(), key=lambda x: x[1], reverse=True)
    
    return [{"appid": appid, "similarity": similarity} for appid, similarity in sorted_recommendations]




def get_user_game_data(user_id=None):
    """
    사용자의 실제 게임 플레이 데이터를 DB에서 가져옴.
    특정 user_id가 제공되면 해당 사용자의 게임 데이터만 반환
    """
    query = """
        SELECT user_id, game_id, playtime
        FROM account_userlibrarygame
    """
    
    if user_id:
        query += " WHERE user_id = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id] if user_id else [])
        rows = cursor.fetchall()

    # 가져온 데이터를 DataFrame으로 변환
    data = pd.DataFrame(rows, columns=["user_id", "appid", "playtime"])

    # 플레이 시간을 0~1 사이의 스케일로 정규화
    data["similarity"] = data["playtime"] / data["playtime"].max() if data["playtime"].max() else 0

    return data

def extract_game_details(document):
    """
    document 컬럼에서 게임의 name, genres, description을 추출하는 함수
    """
    name_match = re.search(r'name:\s(.*?)\s\|', document)
    genres_match = re.search(r'genres:\s(.*?)\s\|', document)
    description_match = re.search(r'description:\s(.*?)(?:\s\||$)', document)

    name = name_match.group(1) if name_match else None
    genres = genres_match.group(1) if genres_match else None
    description = description_match.group(1) if description_match else None

    return name, genres, description

def get_game_details(appid_list):
    """
    특정 게임 ID(appid) 리스트에 해당하는 게임의 이름, 장르, 설명을 가져옴.
    """
    if not appid_list:
        return {}

    # '%s' 대신 개별 값으로 IN 절에 바인딩 (PostgreSQL에서 JSONB 비교)
    placeholders = ', '.join(['%s'] * len(appid_list))  # "%s, %s, %s" 형태로 변환
    query = f"""
        SELECT cmetadata->>'appid' AS appid, document
        FROM langchain_pg_embedding
        WHERE cmetadata->>'appid' IN ({placeholders});
    """

    with connection.cursor() as cursor:
        cursor.execute(query, appid_list)  # 리스트를 개별 값으로 바인딩
        rows = cursor.fetchall()

    game_details = {}
    for row in rows:
        appid, document = row
        name, genres, description = extract_game_details(document)
        game_details[appid] = {"name": name, "genres": genres, "description": description}

    return game_details