from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .ml_utils import get_hybrid_recommendations
from .utils import get_game_details
from django.core.exceptions import ObjectDoesNotExist

from .utils import get_game_details

class HybridRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id

            # 추천된 게임 목록 가져오기
            hybrid_recommendations = get_hybrid_recommendations(user_id, top_n=10)
            appid_list = [str(game["appid"]) for game in hybrid_recommendations]  # appid 리스트 추출

            # 게임 상세 정보 가져오기
            game_details = get_game_details(appid_list)

            # 최종 응답 데이터 구성
            enriched_recommendations = []
            for game in hybrid_recommendations:
                appid = str(game["appid"])
                if appid in game_details:
                    enriched_recommendations.append({
                        "appid": appid,
                        "name": game_details[appid]["name"],
                        "genres": game_details[appid]["genres"],
                        "description": game_details[appid]["description"],
                        "final_score": game["final_score"]
                    })
                else:
                    enriched_recommendations.append({
                        "appid": appid,
                        "name": None,
                        "genres": None,
                        "description": None,
                        "final_score": game["final_score"]
                    })

            return Response({
                "message": "하이브리드 추천 조회 성공",
                "user_id": user_id,
                "recommendations": enriched_recommendations
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": f"추천 시스템 오류: {str(e)}",
                "user_id": user_id if 'user_id' in locals() else None,
                "recommendations": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

