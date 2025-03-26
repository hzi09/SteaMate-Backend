import pickle
from surprise import Dataset, Reader, SVD
import pandas as pd
from .utils import get_user_game_data
import os
from django.conf import settings
from celery import shared_task

@ shared_task
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
    except Exception as e:
        print(f"❌ 협업 필터링 모델 학습 중 오류 발생: {str(e)}")
        raise