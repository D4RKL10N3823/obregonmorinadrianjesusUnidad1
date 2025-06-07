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
from .models import Anime, User, Episode, Comment, Category, HelpMessage
from .forms import SuggestionForm
from django import forms
from django.urls import reverse_lazy

class Login(LoginView):
    model = User
    fields = '__all__'
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('anime_list')


class Signup(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('anime_list')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(Signup, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('anime_list')
        return super(Signup, self).get(*args, **kwargs)
    

class Profile(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['icon']   
    template_name = 'profile.html'
    success_url = reverse_lazy('anime_list')


class AnimeList(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_name = self.request.GET.get('category')
        
        if category_name:
            context['animes'] = context['animes'].filter(categories__name=category_name)
        context['categories'] = Category.objects.all()
        return context


class SearchBar(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self.request.GET.get('search') or ''

        if search_value:
            context['animes'] = context['animes'].filter(title__icontains=search_value)
        context['search_value'] = search_value
        return context
    

class Help(ListView):
    template_name = 'help.html'


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
    

class Suggestion(FormView):
    template_name = 'suggestion.html'
    form_class = SuggestionForm
    success_url = reverse_lazy('suggestion')  

    def form_valid(self, form):
        suggestion = form.save(commit=False)
        if self.request.user.is_authenticated:
            suggestion.user = self.request.user
        suggestion.save()
        return super().form_valid(form)
    

class HelpMessageForm(forms.ModelForm):
    class Meta:
        model = HelpMessage
        fields = ['message']

class HelpChat(LoginRequiredMixin, FormView, ListView):
    template_name = 'help_chat.html'
    form_class = HelpMessageForm
    success_url = reverse_lazy('help_chat')
    model = HelpMessage
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        return HelpMessage.objects.filter(sender=user) | HelpMessage.objects.filter(recipient=user)

    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.sender = self.request.user
        msg.recipient = None 
        msg.save()
        return super().form_valid(form)