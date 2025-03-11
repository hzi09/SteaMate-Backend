from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', views.SignupAPIView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path('<int:pk>/', views.MyPageAPIView.as_view()),
    path("steamlogin/", views.SteamLoginAPIView.as_view()),
    path("steam-callback/", views.SteamCallbackAPIView.as_view()),
    path("steamsignup/", views.SteamSignupAPIView.as_view()),
    path("logout/", views.LogoutAPIView.as_view()),
    path('email-verify/<uidb64>/<token>/', views.EmailVerifyAPIView.as_view(), name='email-verify'),
]