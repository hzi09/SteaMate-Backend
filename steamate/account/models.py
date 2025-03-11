from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator

# Create your models here.

class Genre(models.Model):
    genre_name = models.CharField(max_length=50, unique=True)
    
class Game(models.Model):
    appid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    released_at = models.DateField(blank=True, null=True)
    description = models.TextField(blank = True)
    review_score = models.FloatField(default = 0, blank = True)
    comment = models.TextField(blank = True)
    header_image = models.TextField(blank = True)
    trailer_url = models.TextField(blank = True)
    

class User(AbstractUser):
    
    class GenderChoices(models.IntegerChoices):
        남 = 1, "남"
        여 = 2, "여"
        공개안함 = 3, "공개 안 함"
    
    nickname = models.CharField(max_length=50, unique=True)
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=20, unique=True, validators=[UnicodeUsernameValidator(), MinLengthValidator(5)], verbose_name='username')
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to='user/profile_image/',
        default='user/profile_image/user_default_image.png')
    gender = models.IntegerField(choices = GenderChoices.choices, default=GenderChoices.공개안함)
    birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    steam_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    preferred_genre = models.ManyToManyField(Genre, related_name='users_preferred_genre', blank = True)
    preferred_game = models.ManyToManyField(Game, through='UserPreferredGame', related_name='users_preferred_game', blank = True)
    is_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """is_verified 값이 변경되면 is_active도 동기화"""
        self.is_active = self.is_verified
        super().save(*args, **kwargs)
    

class UserPreferredGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    playtime = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'game')
    
    def __str__(self):
        return f"{self.user.username} - {self.game.title} ({self.playtime}분)"