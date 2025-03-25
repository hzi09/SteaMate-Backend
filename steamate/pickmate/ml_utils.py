import pickle
from surprise import Dataset, Reader, SVD
import pandas as pd
from .utils import get_user_game_data, get_combined_similar_games
import os
from django.conf import settings

def train_collaborative_filtering():
    """
    협업 필터링 모델을 실제 사용자 데이터를 기반으로 학습하고 저장
    """
    try:
        # 사용자 실제 데이터 사용
        user_game_data = get_user_game_data()  # 모든 사용자 데이터 가져오기
        
        if user_game_data.empty:
            raise ValueError("학습할 데이터가 없습니다.")

        reader = Reader(rating_scale=(0, 1))  # similarity는 0~1 사이 값
        data = Dataset.load_from_df(user_game_data[["user_id", "appid", "similarity"]], reader)
        trainset = data.build_full_trainset()

        # SVD 모델 학습
        model = SVD()
        model.fit(trainset)

        # 모델 저장 경로 설정
        model_path = os.path.join(settings.BASE_DIR, 'pickmate', 'models', 'collab_model.pkl')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # 모델 저장
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        print("✅ 협업 필터링 모델이 성공적으로 학습되고 저장되었습니다.")
        return model
    except Exception as e:
        print(f"❌ 협업 필터링 모델 학습 중 오류 발생: {str(e)}")
        raise


def load_collaborative_filtering_model():
    """
    저장된 협업 필터링 모델을 로드
    """
    try:
        model_path = os.path.join(settings.BASE_DIR, 'pickmate', 'models', 'collab_model.pkl')
        if not os.path.exists(model_path):
            raise FileNotFoundError("협업 필터링 모델 파일이 없습니다. 먼저 모델을 학습해주세요.")
            
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        print(f"❌ 협업 필터링 모델 로드 중 오류 발생: {str(e)}")
        raise


def predict_collaborative_score(user_id, game_id, model):
    """
    협업 필터링 모델을 사용하여 특정 게임의 추천 점수를 예측
    """
    try:
        prediction = model.predict(user_id, game_id).est
        return prediction if prediction is not None else 0  # None이면 0 반환
    except Exception:
        return 0  # 예측 실패 시 기본값 반환

def hybrid_score(content_score, collaborative_score, alpha=0.7):
    """
    콘텐츠 기반 추천 점수 (pgvector)와 협업 필터링 점수를 결합
    """
    content_score = content_score if content_score is not None else 0
    collaborative_score = collaborative_score if collaborative_score is not None else 0
    return alpha * content_score + (1 - alpha) * collaborative_score


def get_hybrid_recommendations(user_id, top_n=10):
    """
    사용자의 TOP 10 게임을 기반으로 pgvector 추천 + 협업 필터링을 결합한 최종 추천 리스트 반환
    사용자가 이미 가지고 있는 게임은 제외
    """
    # 사용자가 가지고 있는 게임 목록을 가져오기
    user_owned_games = get_user_game_data(user_id)  # 사용자별 데이터만 가져오기

    # 사용자가 가진 게임의 appid 목록 추출
    owned_game_ids = set(map(str, user_owned_games["appid"]))  # appid를 모두 문자열로 변환

    # pgvector 추천 결과 가져오기
    similar_games = get_combined_similar_games(user_id, top_n)

    # 협업 필터링 모델 로드
    collaborative_model = load_collaborative_filtering_model()  

    hybrid_recommendations = []
    for game in similar_games:
        appid = str(game["appid"])  # appid를 문자열로 변환

        # 사용자가 이미 가지고 있는 게임은 추천 목록에서 제외
        if appid in owned_game_ids:
            print(f"Excluding game {appid} as user already owns it.")  # 제외되는 게임 로그 추가
            continue

        content_score = game["similarity"]
        collaborative_score = predict_collaborative_score(user_id, appid, collaborative_model)
        final_score = hybrid_score(content_score, collaborative_score)

        hybrid_recommendations.append({
            "appid": appid,
            "final_score": final_score
        })

    # 추천 목록 정렬 후 상위 20개 반환
    return sorted(hybrid_recommendations, key=lambda x: x["final_score"], reverse=True)[:20]

