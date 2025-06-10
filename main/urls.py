from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import SiteMapView, AnimeList, AnimeDetail, EpisodeDetail, Login, Signup, Profile, SearchBar, Help, ContactView, SuggestionView, RedirectToConversation, ConversationList, HelpChat

urlpatterns = [
    path('sitemap/', SiteMapView.as_view(), name='sitemap'),

    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="anime_list"), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('', AnimeList.as_view(), name='anime_list'),
    path('search/', SearchBar.as_view(), name='search'),
    path('profile/<int:pk>/', Profile.as_view(), name='profile'),

    path('help/', Help.as_view(), name='help'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('suggestion/', SuggestionView.as_view(), name='suggestion'),
    path('conversations/', ConversationList.as_view(), name='conversation_list'),
    path('help-chat/<int:pk>/', HelpChat.as_view(), name='conversation_detail'),
    path('conversations/redirect/', RedirectToConversation.as_view(), name='home_redirect'),

    path('anime/<str:pk>/', AnimeDetail.as_view(), name='anime_detail'),
    path('<str:anime_title>/episode-<int:episode_number>/', EpisodeDetail.as_view(), name='episode_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)