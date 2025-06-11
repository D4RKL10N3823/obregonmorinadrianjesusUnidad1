from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os

# Define la ruta de subida de íconos de usuario
def user_icon(instance, filename):
    folder_name = instance.username.replace(' ', '_')
    return os.path.join('users', folder_name, filename)

# Define la ruta para las imágenes del anime
def anime_image_upload_path(instance, filename):
    folder_name = instance.title.replace(' ', '_')
    return os.path.join('anime', folder_name, filename)

# Define la ruta para la imagen del capitulo
def anime_image_episode(instance, filename):
    folder_name = instance.anime.title.replace(' ', '_')
    episode_folder = f"episode_{instance.episode_number}"
    return os.path.join('anime', folder_name, 'episodes', episode_folder, filename)


# Modelo de Usuario 
class User(AbstractUser):
    icon = models.ImageField(upload_to=user_icon, default="users/default.png", blank=True)
    favorite_animes = models.ManyToManyField('Anime', related_name='favorited_by', blank=True)

    def __str__(self):
        return self.username

    # Elimina la foto de perfil anterior si cambia
    def save(self, *args, **kwargs):
        try:
            old_user = User.objects.get(pk=self.pk)
            if old_user.icon and old_user.icon.url != self.icon.url and "default.png" not in old_user.icon.url:
                old_user.icon.delete(save=False)
        except User.DoesNotExist:
            pass
        super().save(*args, **kwargs)

#  Modelo de las categorias
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Modelo de los Animes
class Anime(models.Model):
    title = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField()
    image_detail = models.ImageField(upload_to=anime_image_upload_path, null=True, blank=True)
    image_card = models.ImageField(upload_to=anime_image_upload_path, null=True, blank=True)
    release_date = models.DateField()
    total_episodes = models.IntegerField()
    like_count = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name='animes', blank=True)

    def __str__(self):
        return self.title

# Modelo de los episodios, que esta relacionado por anime
class Episode(models.Model):
    title = models.CharField(max_length=255, primary_key=True, unique=True)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField()
    release_date = models.DateField()
    video_url = models.URLField(null=True, blank=True, help_text="URL server")
    image_url = models.ImageField(upload_to=anime_image_episode, null=True, blank=True)

    class Meta:
        unique_together = ('anime', 'episode_number')

    def __str__(self):
        return f"{self.anime.title} - Episode {self.episode_number}"
    
# Modelo de los conmentarios, que esta relacionado por anime y episodio
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='comments', null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.anime.title} - {self.episode}"
    
# Modelo de las sugerencias
class Suggestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sugerencia de {self.user.username if self.user else 'Anónimo'}"
    
# Modelo de las conversaciones
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')

    def __str__(self):
        return f"Conversación con {self.user.username}"

# Modelo del chat de ayuda
class HelpMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.sender.username} para {self.recipient.username if self.recipient else 'todos'}"