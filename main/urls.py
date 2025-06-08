from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import AnimeList, AnimeDetail, EpisodeDetail, Login, Signup, Profile, SearchBar, Suggestion, RedirectToConversation, ConversationList, HelpChat

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="anime_list"), name='logout'),

    path('', AnimeList.as_view(), name='anime_list'),
    path('search/', SearchBar.as_view(), name='search'),
    path('profile/<int:pk>/', Profile.as_view(), name='profile'),

    path('suggestion/', Suggestion.as_view(), name='suggestion'),
    path('conversations/', ConversationList.as_view(), name='conversation_list'),
    path('help-chat/<int:pk>/', HelpChat.as_view(), name='conversation_detail'),
    path('conversations/redirect/', RedirectToConversation.as_view(), name='home_redirect'),

    path('anime/<str:pk>/', AnimeDetail.as_view(), name='anime_detail'),
    path('<str:anime_title>/episode-<int:episode_number>/', EpisodeDetail.as_view(), name='episode_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)