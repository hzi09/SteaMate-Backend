from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Genre(models.Model):
    genre_name = models.CharField(max_length=50)
    
class Game(models.Model):
    appid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    released_at = models.DateField()

class User(AbstractUser):
    
    class GenderChoices(models.IntegerChoices):
        남 = 1, "남"
        여 = 2, "여"
        공개안함 = 3, "공개 안 함"
    
    nickname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to='user/profile_image/',
        default='user/profile_image/user_default_image.png')
    gender = models.IntegerField(choices = GenderChoices.choices, default=GenderChoices.공개안함)
    birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    steam_id = models.CharField(max_length=20, blank=True)
    
    preferred_genre = models.ManyToManyField(Genre, related_name='preferred_genre')
    preferred_game = models.ManyToManyField(Game, related_name='preferred_game')
    
    def __str__(self):
        return self.username