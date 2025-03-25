from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .ml_utils import get_hybrid_recommendations
from django.core.exceptions import ObjectDoesNotExist

class HybridRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id

            # 가장 많이 플레이한 10개 게임을 기반으로 추천 수행
            hybrid_recommendations = get_hybrid_recommendations(user_id, top_n=10)

            return Response({
                "message": "하이브리드 추천 조회 성공",
                "user_id": user_id,
                "recommendations": hybrid_recommendations
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "message": f"추천 시스템 오류: {str(e)}",
                "user_id": user_id if 'user_id' in locals() else None,
                "recommendations": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

