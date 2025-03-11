from rest_framework import serializers
from .models import User, Genre, Game

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'username', 'password', 'email', 'birth', 'gender',]
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            birth=validated_data['birth'],
            gender=validated_data['gender'],
        )
        user.set_password(validated_data['password'])
        user.is_verified = False # 이메일 인증 전까지 False
        user.save()
        return user
        

class UserUpdateSerializer(serializers.ModelSerializer):
    preferred_genre = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, required=False
    )
    preferred_game = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(), many=True, required=False
    )
    
    
    class Meta:
        model = User
        fields = ['nickname', 'email', 'profile_image', 'preferred_genre', 'preferred_game', 'steam_id']
        extra_kwargs = {'profile_image': {'required': False},
                        'steam_id': {'required': False}
        }
        
    def update(self, instance, validated_data):
        """유저 정보 수정 로직 (ManyToManyField 처리 포함)"""
        preferred_genres = validated_data.pop("preferred_genre", None)
        preferred_games = validated_data.pop("preferred_game", None)

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)

        # ManyToMany 필드 업데이트 (선택된 경우만 업데이트)
        if preferred_genres is not None:
            instance.preferred_genre.set(preferred_genres)

        if preferred_games is not None:
            instance.preferred_game.set(preferred_games)

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
        """비밀번호 일치 확인"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        """회원가입 시 비밀번호 해싱"""
        validated_data.pop("confirm_password")  # `confirm_password` 필드는 DB에 저장하지 않음
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        user.is_verified = True # 이메일 인증 생략략

        if password:
            user.set_password(password)  # 비밀번호 해싱

        user.save()
        return user