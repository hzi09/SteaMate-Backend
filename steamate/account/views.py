from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import (User, UserPreferredGame, Game, Genre, UserPreferredGenre, UserLibraryGame,
                     UserPreferredTag, Tag, GameTag)
from .serializers import (CreateUserSerializer, UserUpdateSerializer,
                          SteamSignupSerializer, CustomTokenObtainPairSerializer)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.conf import settings
import urllib.parse
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError
import os
from dotenv import load_dotenv
from .utils import fetch_steam_library, get_or_create_game, get_or_create_genre
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.timezone import now
import logging
from django.db.utils import IntegrityError
from rest_framework_simplejwt.views import TokenObtainPairView
from .tasks import send_verification_email, fetch_and_save_user_games

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SignupAPIView(APIView):
    """일반 사용자 회원가입 API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            api_prefix = "/api/v1/account/"
            
            # 이메일 인증 토큰 생성
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_url = f"{settings.SITE_URL}/{reverse('account:verify-email', kwargs={'uidb64': uid, 'token': token}).replace(api_prefix, '')}"
            # 이메일 전송
            
            subject="이메일 인증"
            text_content =f"이메일 인증을 위해 다음 링크를 클릭해주세요: {verification_url}"
            html_content=f"""
            <p>이메일 인증을 위해 아래 링크를 클릭해주세요.</p>
            <p><a href="{verification_url}" target="_blank">{verification_url}</a></p>
            <p>감사합니다!</p>
            """
            
            send_verification_email.delay(subject, text_content, html_content, user.email)
            return Response({
                "message":"회원가입 완료. 이메일을 확인하고 인증을 완료하세요.",
                "email_verification_url":verification_url
                }, status=status.HTTP_201_CREATED)


class EmailVerifyAPIView(APIView):
    """이메일 인증 API"""
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token):
        try:
            # uidb64를 다시 pk 값으로 돌려 user 확인
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
            
            if user.is_verified:
                # return redirect('/?error=already-verified')
                return Response({"success":True,
                                "message": "이미 인증된 계정입니다."
                                }, status=status.HTTP_200_OK)
            
            if user.is_verification_expired():
                user.delete()
                # return redirect('/?error=time-over')
                return Response({"success": False, 
                                "error": "인증 시간이 만료되었습니다. 다시 회원가입해주세요."
                                }, status=status.HTTP_400_BAD_REQUEST)
            
            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                # return redirect('/')
                return Response({"success": True, 
                                "message":"이메일 인증이 완료되었습니다."
                                }, status=status.HTTP_200_OK)
            else:
                # return redirect('/?error=invalid-token')
                return Response({"success": False, 
                                "error":"유효하지 않은 토큰입니다."
                                }, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # return redirect('/?error=bad-request')
            return Response({"success": False,
                            "error":"잘못된 요청입니다."
                            }, status=status.HTTP_400_BAD_REQUEST)

class SteamLoginAPIView(APIView):
    """Steam OpenID 로그인 요청"""
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.steam_id:
                return Response({"error": "이미 Steam 계정 연동이 되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        """GET 요청 시 Steam 로그인 페이지로 리디렉션"""
        steam_openid_url = "https://steamcommunity.com/openid/login"
        
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": f"{settings.SITE_URL}/steam-callback/",
            "openid.realm": settings.SITE_URL,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }

        steam_login_url = f"{steam_openid_url}?{urllib.parse.urlencode(params)}"
        return Response({"steam_login_url":steam_login_url}, status=status.HTTP_200_OK)

class SteamCallbackAPIView(APIView):
    """Steam 로그인 Callback API (Steam ID 검증)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Steam 로그인 성공 후, OpenID 검증"""

        # GET 파라미터를 dict 형태로 변환
        openid_params = request.GET
        
        # 필수 OpenID 파라미터 유지
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

        # Steam OpenID 검증 요청 (POST 사용)
        response = requests.post(steam_openid_url, data=steam_openid_params)

        # Steam 응답 처리
        response_text = response.text.strip()

        # Steam 인증 실패 시
        if "is_valid:true" not in response_text:
            return Response(
                {"error": "Steam 인증 실패", "steam_response": response_text[:200]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Steam ID 추출 (예외 처리 강화)
        steam_id_url = openid_params.get("openid.claimed_id", "")
        if not steam_id_url or not steam_id_url.startswith("https://steamcommunity.com/openid/id/"):
            return Response({"error": "잘못된 Steam ID 응답"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            steam_id = steam_id_url.split("/")[-1]
            if not steam_id.isdigit():
                raise ValueError("Steam ID가 숫자가 아닙니다.")
        except Exception as e:
            return Response({"error": f"Steam ID 처리 중 오류 발생: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Steam ID 연동
        user = request.user
        if request.user.is_authenticated:
            if user.steam_id:
                return Response({"error": "이미 Steam 계정 연동이 되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(steam_id=steam_id).exists():
                return Response({"error": "이미 다른 계정에 연동된 Steam ID입니다."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "new_user":False,
                "message": "Steam 계정 호출 완료",
                "steam_id":steam_id
                }, status=status.HTTP_200_OK)


        # Steam ID 로그인
        if User.objects.filter(steam_id=steam_id).exists():
            return Response({
                "new_user":False,
                "message": "Steam 계정 호출 완료",
                "steam_id":steam_id
                }, status=status.HTTP_202_ACCEPTED)

        # Steam ID 회원가입
        return Response({
            "new_user":True,
            "message":"Steam 계정 호출 완료",
            "steam_id":steam_id
            }, status=status.HTTP_200_OK)



class SteamIDLoginAPIView(APIView):
    """Steam ID 로그인 API"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Steam ID를 사용하여 로그인"""
        steam_id = request.data.get("steam_id")

        if not steam_id or not steam_id.isdigit():
            return Response({"error": "올바른 Steam ID를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(steam_id=steam_id).first()

        if not user:
            return Response({"error": "등록되지 않은 Steam ID입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 로그인 후 JWT 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Steam 로그인 성공",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id
        }, status=status.HTTP_200_OK)

class SteamSignupAPIView(APIView):
    """Steam 회원가입 (추가 정보 입력)"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Steam 회원가입: 추가 정보 입력 후 계정 생성"""
        serializer = SteamSignupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            
            steam_id = serializer.validated_data.get("steam_id")
            if not steam_id or not steam_id.isdigit():
                return Response({"error": "올바른 Steam ID를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)
            
            steam_name = None
            steam_profile_url = None
            steam_avatar = None
            warning = None
            
            steam_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steam_id}"
            
            try:
                response = requests.get(steam_url, timeout=5)
                response.raise_for_status()
                players = response.json().get("response",{}).get("players",[])
                
                if players:
                    steam_date = players[0]
                    steam_name = steam_date.get("personaname")
                    steam_profile_url = steam_date.get("profileurl")
                    steam_avatar = steam_date.get("avatar")
                else:
                    warning = "Steam 프로필이 비공개 상태입니다. 일부 정보가 표시되지 않을 수 있습니다."
            except Exception as e:
                warning = f"Steam API 요청 실패: {str(e)}"
            
            user = serializer.save(
                steam_name = steam_name,
                steam_profile_url = steam_profile_url,
                steam_avatar = steam_avatar
                )
            
            # JWT 토큰 발급
            refresh = RefreshToken.for_user(user)
            response_data = {
                **serializer.data,
                "message": "Steam 회원가입 완료",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id
            }
            if warning:
                response_data["warning"] = warning
            return Response(response_data, status=status.HTTP_201_CREATED)


class SteamLinkAPIView(APIView):
    """Steam 계정 연동 API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Steam 계정을 기존 유저 계정에 연동"""
        steam_id = request.data.get("steam_id")
    
        if not steam_id or not steam_id.isdigit():
            return Response({"error":"올바른 Steam ID를 입력하세요"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
        user = request.user
    
        # 다른 계정에 연동된 Steam ID 인지 확인
        if User.objects.filter(steam_id=steam_id).exists():
            return Response({"error":"이미 다른 계정에 연동된 Steam ID입니다."},status=status.HTTP_403_FORBIDDEN)
    
        # 현재 로그인한 유저에 Steam ID 정보가 있는지 확인
        if user.steam_id:
            return Response({"error":"이미 Steam ID가 연동되어있습니다."}, status=status.HTTP_409_CONFLICT)

        steam_name = None
        steam_profile_url = None
        steam_avatar = None
        warning = None
        
        steam_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steam_id}"
    
        try:
            response = requests.get(steam_url, timeout=5)
            response.raise_for_status()
            players = response.json().get("response",{}).get("players",[])
            
            if players:
                steam_data = players[0]
                steam_name = steam_data.get("personaname")
                steam_profile_url = steam_data.get("profileurl")
                steam_avatar = steam_data.get("avatar")
            else:
                warning = "Steam 프로필이 비공개 상태입니다. 일부 정보가 표시되지 않을 수 있습니다."
        except Exception as e:
            warning = f"Steam API 요청 실패: {str(e)}"
    
    
        user.steam_id = steam_id
        user.steam_name = steam_data.get("personaname")
        user.steam_profile_url = steam_data.get("profileurl")
        user.steam_avatar = steam_data.get("avatar")
        user.save()
        
        response_data = {
            "message": "Steam 계정 연동 완료",
        }
        if warning:
            response_data["warning"] = warning
        return Response(response_data, status=status.HTTP_201_CREATED)



class MyPageAPIView(APIView):
    """사용자 정보 조회, 수정, 삭제 API"""
    def get_permissions(self):
        """요청 방식(GET, PUT, DELETE)에 따라 다른 권한을 적용"""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_user(self, pk):
        return get_object_or_404(User, pk=pk)
        
    def get(self, request, pk):
        """사용자 정보 조회"""
        
        user = self.get_user(pk)
        serializer = UserUpdateSerializer(user)
        data = serializer.data
        
        # Steam API로 사용자 정보 가져오기
        if user.steam_id:
            data["steam_profile"] = {
                "personname":user.steam_name,
                "avatar":user.steam_avatar,
                "profileurl":user.steam_profile_url
            }
        
        data["preferred_tag"] = [tag.tag.name for tag in user.preferred_tags.all()]
        data["preferred_genre"] = [genre.genre.genre_name for genre in user.preferred_genres.all()]
        data["preferred_game"] = [game.game.title for game in user.preferred_games.all()]
        data["library_games"] = [{"title":lib.game.title, "playtime":lib.playtime} for lib in user.library_games.all()]
        
        return Response(data, status=status.HTTP_200_OK)


    def put(self, request, pk):
        """사용자 일반 정보 수정"""
        if pk != request.user.pk:
            return Response({"error": "You do not have permission to this page"},status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_user(pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """사용자의 선호 게임 + 장르 수정"""
        if pk != request.user.pk:
            return Response({"error": "You do not have permission to this page"},status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_user(pk)
        preferred_game_titles = request.data.get("preferred_game", [])
        
        if not isinstance(preferred_game_titles, list):
            return Response({"error": "preferred_game은 리스트여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 기존 선호 게임/장르 제거
        UserPreferredGame.objects.filter(user=user).delete()
        UserPreferredGenre.objects.filter(user=user).delete()
        UserPreferredTag.objects.filter(user=user).delete()
        
        # 게임 title -> Game 객체 일괄 조회
        games = Game.objects.filter(title__in=preferred_game_titles)
        game_dict = {game.title:game for game in games}
        
        # 선호 게임 저장 준비
        preferred_game_objs = []
        genre_name_set = set()
        tag_name_set = set()
        
        for title in preferred_game_titles:
            game = game_dict.get(title)
            if not game:
                continue
            preferred_game_objs.append(UserPreferredGame(user=user, game=game))
            
            # 장르 문자열 -> 리스트
            genre_names = [g.strip() for g in game.genre.split(",") if g.strip()]
            genre_name_set.update(genre_names)
            
            # 선호 태그 저장
            tag_names = [tag.tag.name for tag in game.tags.all()]
            tag_name_set.update(tag_names)
            
        
        preferred_genre_objs = []
        for genre_name in genre_name_set:
            genre, _ = Genre.objects.get_or_create(genre_name=genre_name)
            preferred_genre_objs.append(UserPreferredGenre(user=user, genre=genre))
        
        
        preferred_tag_objs = []
        for tag_name in tag_name_set:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            preferred_tag_objs.append(UserPreferredTag(user=user, tag=tag))
        
        # bulk 저장
        if preferred_game_objs:
            UserPreferredGame.objects.bulk_create(preferred_game_objs)
        if preferred_genre_objs:
            UserPreferredGenre.objects.bulk_create(preferred_genre_objs)
        if preferred_tag_objs:
            UserPreferredTag.objects.bulk_create(preferred_tag_objs)
        
        return Response({
            "message": "선호 게임/장르 수정 완료",
                "preferred_games": preferred_game_titles,
                "preferred_genres": list(genre_name_set),
                "preferred_tags": list(tag_name_set)
            }, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """사용자 탈퇴 및 정보 삭제"""
        if pk != request.user.pk:
            return Response({"error": "You do not have permission to delete this user"},status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_user(pk)
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"error":"Refresh token is required for account deletion."}, status=status.HTTP_400_BAD_REQUEST)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        
        return Response({"message":"withdrawal"},status=status.HTTP_204_NO_CONTENT)


class GetSteamLibraryAPIView(APIView):
    """
    Stema 라이브러리를 가져오는 API
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        user.is_syncing = True
        user.save()
        
        result = fetch_and_save_user_games.delay(request.user.id)
        return Response({"message":"Steam 라이브러리 연동 중입니다."}, status=status.HTTP_201_CREATED)

class LogoutAPIView(APIView):
    """
    로그아웃 API
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            # refresh_token이 없을 때
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # 기타 예외 발생 시
            return Response({"error": f"Token processing error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)