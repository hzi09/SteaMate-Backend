from django.urls import path
from .views import HybridRecommendationAPIView

urlpatterns = [
    path('recommend/', HybridRecommendationAPIView.as_view(), name='recommend'),
]
