from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import AnimeList, AnimeDetail, EpisodeDetail, Login, Register, UpdateUser

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="anime_list"), name='logout'),
    path('update_user/<int:pk>', UpdateUser.as_view(), name='update_user'),
    path('', AnimeList.as_view(), name='anime_list'),
    path('anime/<str:pk>/', AnimeDetail.as_view(), name='anime_detail'),
    path('<str:anime_title>/episodio_<int:episode_number>/', EpisodeDetail.as_view(), name='episode_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)