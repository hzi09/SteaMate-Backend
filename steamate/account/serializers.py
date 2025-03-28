from rest_framework import serializers
from .models import User, Genre, Game
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        
        # 먼저 유저가 존재하는지 확인
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("아이디 혹은 비밀번호가 잘못되었습니다.", code="invalid_credentials")

        # 이메일 인증 여부 확인
        if not user.is_verified:
            raise AuthenticationFailed("이메일 인증이 필요합니다.", code="email_not_verified")

        # 유저가 존재하면 authenticate() 실행
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("아이디 혹은 비밀번호가 잘못되었습니다.", code="invalid_credentials")

        return super().validate(attrs)


class CreateUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only = True, required=True)

    class Meta:
        model = User
        fields = ['nickname', 'username', 'password', 'confirm_password', 'email', 'birth', 'gender',]
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        """비밀번호 일치 확인 및 중복된 username/nickname 확인"""
        nickname = data.get("nickname")
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not all([password, confirm_password]):
            raise serializers.ValidationError({"confirm_password": "비밀번호와 비밀번호 확인을 모두 입력해야 합니다."})

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})

        self.delete_expired_user(username = username, nickname = nickname)
        
        return data
        
    def delete_expired_user(self, username = None, nickname=None):
        # 중복된 username이 있고, 인증이 안 된 상태에 확인 기간이 만료된 상태라면 삭제
        try:
            if username:
                existing_user = User.objects.get(username = username)
                if existing_user.is_verification_expired():
                    existing_user.delete()
        except User.DoesNotExist:
            pass
        # 중복된 nickname이 있고, 인증이 안 된 상태에 확인 기간이 만료된 상태라면 삭제
        try:
            if nickname:
                existing_user = User.objects.get(nickname = nickname)
                if existing_user.is_verification_expired():
                    existing_user.delete()
        except User.DoesNotExist:
            pass

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            birth=validated_data['birth'],
            gender=validated_data['gender'],
            is_verified=False  # 이메일 인증 전까지 False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """유저 정보 수정 Serializer"""   
    class Meta:
        model = User
        fields = ['nickname', 'profile_image',  'steam_id', 'is_syncing']
        extra_kwargs = {'profile_image': {'required': False},
                        'steam_id': {'required': False},
                        'is_syncing': {'read_only': True}
        }


    def update(self, instance, validated_data):
        """유저 정보 수정 로직"""

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)

        instance.save()
        return instance
    


class SteamSignupSerializer(serializers.ModelSerializer):
    """Steam 회원가입 Serializer"""
    confirm_password = serializers.CharField(write_only=True)  # 비밀번호 확인 필드 추가

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'birth', 'gender', 'steam_id', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        nickname = data.get("nickname")
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        """비밀번호 일치 확인"""
        if not all([password, confirm_password]):
            raise serializers.ValidationError({"confirm_password": "비밀번호와 비밀번호 확인을 모두 입력해야 합니다."})
        
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})
        
        if not data.get("steam_id"):
            raise serializers.ValidationError({"steam_id": "Steam ID는 필수입니다."})
        
        self.delete_expired_user(username=username, nickname = nickname)
        
        return data
        
    def delete_expired_user(self, username = None, nickname = None):
        # 중복된 username이 있고, 인증이 안 된 상태에 확인 기간이 만료된 상태라면 삭제
        try:
            if username:
                existing_user = User.objects.get(username = username)
                if existing_user.is_verification_expired():
                    existing_user.delete()
        except User.DoesNotExist:
            pass

        # 중복된 nickname이 있고, 인증이 안 된 상태에 확인 기간이 만료된 상태라면 삭제
        try:
            if nickname:
                existing_user = User.objects.get(nickname = nickname)
                if existing_user.is_verification_expired():
                    existing_user.delete()
        except User.DoesNotExist:
            pass

    def create(self, validated_data):
        """회원가입 시 비밀번호 해싱"""
        validated_data.pop("confirm_password")  # `confirm_password` 필드는 DB에 저장하지 않음
        password = validated_data.pop("password", None)
        user = User(
            **validated_data,
            is_verified = True # 이메일 인증 생략
            )

        if password:
            user.set_password(password)  # 비밀번호 해싱

        user.save()
        return user