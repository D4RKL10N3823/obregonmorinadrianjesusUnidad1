from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os

def user_icon(instance, filename):
    folder_name = instance.username.replace(' ', '_')
    return os.path.join('users', folder_name, filename)

def anime_image_upload_path(instance, filename):
    folder_name = instance.title.replace(' ', '_')
    return os.path.join('anime', folder_name, filename)

def anime_image_episode(instance, filename):
    folder_name = instance.anime.title.replace(' ', '_')
    episode_folder = f"episode_{instance.episode_number}"
    return os.path.join('anime', folder_name, 'episodes', episode_folder, filename)

def anime_video_episode(instance, filename):
    folder_name = instance.anime.title.replace(' ', '_')
    episode_folder = f"episode_{instance.episode_number}"
    return os.path.join('anime', folder_name, 'episodes', episode_folder, filename)


class User(AbstractUser):
    icon = models.ImageField(upload_to=user_icon, default="media/users/default.png", blank=True)
    favorite_animes = models.ManyToManyField('Anime', related_name='favorited_by', blank=True)

    def __str__(self):
        return self.username


class Anime(models.Model):
    title = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField()
    image_detail = models.ImageField(upload_to=anime_image_upload_path, null=True, blank=True)
    image_card = models.ImageField(upload_to=anime_image_upload_path, null=True, blank=True)
    release_date = models.DateField()
    genre = models.CharField(max_length=255)
    total_episodes = models.IntegerField()
    like_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Episode(models.Model):
    title = models.CharField(max_length=255, primary_key=True, unique=True)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField()
    release_date = models.DateField()
    video_url = models.FileField(upload_to=anime_video_episode, null=True, blank=True)
    image_url = models.ImageField(upload_to=anime_image_episode, null=True, blank=True)

    class Meta:
        unique_together = ('anime', 'episode_number')

    def __str__(self):
        return f"{self.anime.title} - Episode {self.episode_number}"
    

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='comments', null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.anime.title} - {self.episode}"