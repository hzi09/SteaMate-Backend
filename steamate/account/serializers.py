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
        """🔥 유저 정보 수정 로직 (ManyToManyField 처리 포함)"""
        preferred_genres = validated_data.pop("preferred_genre", None)
        preferred_games = validated_data.pop("preferred_game", None)

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)

        # 🔥 ManyToMany 필드 업데이트 (선택된 경우만 업데이트)
        if preferred_genres is not None:
            instance.preferred_genre.set(preferred_genres)

        if preferred_games is not None:
            instance.preferred_game.set(preferred_games)

        instance.save()
        return instance
    

class SteamLoginSerializer(serializers.Serializer):
    """Steam 로그인 Serializer"""
    steam_id = serializers.CharField(required=True)

    def validate(self, attrs):
        steam_id = attrs.get("steam_id")

        # Steam ID가 이미 존재하는지 확인
        user = User.objects.filter(steam_id=steam_id).first()

        if not user:
            user = User.objects.create(steam_id=steam_id)
            return {"user": user, "created": True}
        
        return {"user": user, "created": False}

class SteamSignupSerializer(serializers.ModelSerializer):
    """Steam 회원가입 Serializer (추가 정보 입력)"""
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'birth', 'gender', 'steam_id']
        extra_kwargs = {'steam_id': {'read_only': True}}

    def validate_email(self, value):
        """이메일 중복 체크"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def update(self, instance, validated_data):
        """추가 정보 업데이트"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()