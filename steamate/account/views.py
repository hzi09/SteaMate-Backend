from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from .serializers import CreateUserSerializer, UserUpdateSerializer, SteamLoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.conf import settings
import urllib.parse
from rest_framework_simplejwt.tokens import RefreshToken
import requests

class SignupAPIView(APIView):
    """일반 사용자 회원가입 API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class SteamLoginAPIView(APIView):
    """Steam OpenID 로그인 요청"""
    permission_classes = [AllowAny]

    def get(self, request):
        """GET 요청 시 Steam 로그인 페이지로 리디렉션"""
        steam_openid_url = "https://steamcommunity.com/openid/login"
        
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": f"{settings.SITE_URL}/api/v1/account/steam-callback/",
            "openid.realm": settings.SITE_URL,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }

        steam_login_url = f"{steam_openid_url}?{urllib.parse.urlencode(params)}"
        return redirect(steam_login_url)
            
class SteamCallbackAPIView(APIView):
    """🔥 Steam 로그인 Callback API (Steam ID 검증)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Steam 로그인 성공 후, OpenID 검증"""

        # ✅ GET 파라미터를 dict 형태로 변환
        openid_params = request.GET.dict()
        
        # ✅ 필수 OpenID 파라미터 유지
        steam_openid_params = {
            "openid.ns": openid_params.get("openid.ns", ""),
            "openid.mode": "check_authentication",
            "openid.op_endpoint": openid_params.get("openid.op_endpoint", ""),
            "openid.claimed_id": openid_params.get("openid.claimed_id", ""),
            "openid.identity": openid_params.get("openid.identity", ""),
            "openid.return_to": openid_params.get("openid.return_to", ""),
            "openid.response_nonce": openid_params.get("openid.response_nonce", ""),
            "openid.assoc_handle": openid_params.get("openid.assoc_handle", ""),
            "openid.signed": openid_params.get("openid.signed", ""),
            "openid.sig": openid_params.get("openid.sig", ""),
        }

        steam_openid_url = "https://steamcommunity.com/openid/login"

        # ✅ Steam OpenID 검증 요청 (POST 사용)
        response = requests.post(steam_openid_url, data=steam_openid_params)

        # ✅ Steam 응답 처리
        response_text = response.text.strip()
        print("🔍 Steam OpenID 응답 (첫 50자):", response_text[:50])

        # ❌ Steam 인증 실패 시
        if "is_valid:true" not in response_text:
            return Response(
                {"error": "Steam 인증 실패", "steam_response": response_text[:200]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Steam ID 추출 (예외 처리 강화)
        steam_id_url = openid_params.get("openid.claimed_id", "")
        if not steam_id_url.startswith("https://steamcommunity.com/openid/id/"):
            return Response({"error": "잘못된 Steam ID 응답"}, status=status.HTTP_400_BAD_REQUEST)

        steam_id = steam_id_url.split("/")[-1]

        # ✅ DB에서 해당 Steam ID가 존재하는지 확인
        user = User.objects.filter(steam_id=steam_id).first()

        if user:
            # ✅ 기존 회원이면 JWT 발급 후 로그인 처리
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Steam 로그인 성공",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "redirect_url": "/"  # 홈으로 리다이렉트
            }, status=status.HTTP_200_OK)
        
        # 🚀 신규 회원이면 추가 정보 입력 필요 → 회원가입 페이지로 리다이렉트
        return Response({
            "message": "Steam 인증 성공. 추가 정보 입력이 필요합니다.",
            "steam_id": steam_id,
            "needs_update": True,
            "redirect_url": "/signup"  # 회원가입 페이지로 이동
        }, status=status.HTTP_201_CREATED)



class SteamSignupAPIView(APIView):
    """🔥 Steam 회원가입 (추가 정보 입력)"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Steam 회원가입: 추가 정보 입력 후 계정 생성"""
        steam_id = request.data.get("steam_id")
        username = request.data.get("username")  # 사용자가 입력한 username
        nickname = request.data.get("nickname")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        email = request.data.get("email")
        birth = request.data.get("birth")
        gender = request.data.get("gender")

        # 필수 입력값 확인
        if not all([steam_id, username, nickname, email, birth, gender, password, password2]):
            return Response({"error": "모든 정보를 입력해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 일치 확인
        if password != password2:
            return Response({"error": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ username 중복 확인 → 중복이면 회원가입 불가 (다른 username 사용 유도)
        if User.objects.filter(username=username).exists():
            return Response({"error": "이미 사용 중인 username입니다. 다른 이름을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 이미 가입된 Steam ID인지 확인
        if User.objects.filter(steam_id=steam_id).exists():
            return Response({"error": "이미 가입된 Steam 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 유저 생성
        user = User.objects.create_user(
            steam_id=steam_id,
            username=username,  # 입력한 username 그대로 사용
            nickname=nickname,
            email=email,
            birth=birth,
            gender=gender,
        )
        user.set_password(password)
        user.save()

        # ✅ JWT 발급 후 로그인 처리
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Steam 회원가입 완료",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "redirect_url": "/"
        }, status=status.HTTP_201_CREATED)



class MyPageAPIView(APIView):
    """사용자 정보 조회, 수정, 삭제 API"""
    def get_permissions(self):
        """요청 방식(GET, PUT, DELETE)에 따라 다른 권한을 적용"""
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_user(self, pk):
        return get_object_or_404(User, pk=pk)
        
    def get(self, request, pk):
        """사용자 정보 조회"""
        user = self.get_user(pk)
        serializer = UserUpdateSerializer(user)
        response_data = serializer.data
        response_data['preferred_genre'] = [
            genre.genre_name for genre in user.preferred_genre.all()
        ]
        response_data['preferred_game'] = [
            game.title for game in user.preferred_game.all()
        ]
        
        return Response(serializer.data)
    
    def put(self, request,pk):
        """사용자 정보 수정"""
        if pk != request.user.pk:
            return Response({"error": "You do not have permission to this page"},status=status.HTTP_403_FORBIDDEN)
        user = self.get_user(request.user.pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    def delete(self, request, pk):
        """사용자 탈퇴 및 정보 삭제"""
        if pk != request.user.pk:
            return Response({"error": "You do not have permission to delete this user"},status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_user(request.user.pk)
        user.delete()
        return Response({"message":"withdrawal"},status=status.HTTP_204_NO_CONTENT)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "token error."}, status=status.HTTP_400_BAD_REQUEST
            )