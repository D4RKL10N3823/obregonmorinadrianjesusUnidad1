from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CustomUserCreationForm
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Anime, User, Episode, Comment
from django.urls import reverse_lazy


class Login(LoginView):
    model = User
    fields = '__all__'
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('anime_list')


class Register(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('anime_list')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(Register, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('anime_list')
        return super(Register, self).get(*args, **kwargs)
    

class UpdateUser(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['icon']
    template_name = 'update_user.html'
    success_url = reverse_lazy('anime_list')


class AnimeList(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self.request.GET.get('search') or ''
        
        if search_value:
            context['animes'] = context['animes'].filter(title__icontains=search_value)
        context['search_value'] = search_value
        return context



class AnimeDetail(LoginRequiredMixin, DetailView):
    model = Anime
    context_object_name = 'anime'
    template_name = 'anime_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['episodes'] = Episode.objects.filter(anime=self.object)
        return context


class EpisodeDetail(LoginRequiredMixin, DetailView):
    model = Episode
    context_object_name = 'episode'
    template_name = 'episode_detail.html'
    
    def get_object(self):
        anime_title = self.kwargs['anime_title']
        episode_number = self.kwargs['episode_number']
        anime = get_object_or_404(Anime, title=anime_title)
        return get_object_or_404(Episode, anime=anime, episode_number=episode_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anime'] = self.object.anime
        context['comments'] = Comment.objects.filter(episode=self.object)
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        content = request.POST.get('content')
        if request.user.is_authenticated and content:
            Comment.objects.create(
                user=request.user,
                anime=self.object.anime,
                episode=self.object,
                content=content
            )
        return HttpResponseRedirect(self.request.path_info)