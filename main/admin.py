from django.contrib import admin
from .models import Anime, Episode, Comment, Category, User

# Se agregan los modelos al panel del Admin
admin.site.register(User) 
admin.site.register(Anime)
admin.site.register(Episode)
admin.site.register(Comment)
admin.site.register(Category)