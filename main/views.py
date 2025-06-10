from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CustomUserCreationForm
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Anime, User, Episode, Comment, Category, Conversation, Suggestion
from .forms import SuggestionForm, HelpMessageForm
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .utils.recaptcha import verify_recaptcha
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView  
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import EmailMessage


class SiteMapView(TemplateView):  
    template_name = 'sitemap.html'  


class Login(LoginView):
    model = User
    fields = '__all__'
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('anime_list')


class Signup(FormView):
    template_name = 'signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('anime_list')

    def form_valid(self, form):
        token = self.request.POST.get("g-recaptcha-response")
        if not token or not verify_recaptcha(token):
            messages.error(self.request, "Error de reCAPTCHA. Intenta de nuevo.")
            return self.form_invalid(form)

        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RECAPTCHA_SITE_KEY'] = settings.RECAPTCHA_SITE_KEY
        return context
    
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


class Help(View):
    def get(self, request):
        return render(request, 'help.html') 


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
    

class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact') 

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject'] or 'Contacto TakosuAnime'
        message = form.cleaned_data['message']
        body = (
            f"Nombre: {name}\n"
            f"Email de contacto: {email}\n\n"
            f"{message}"
        )

        correo = EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=[settings.DEFAULT_FROM_EMAIL], headers={'Reply-To': form.cleaned_data['email']})
        correo.send(fail_silently=False)
        return super().form_valid(form)



class SuggestionView(LoginRequiredMixin, FormView):
    template_name = 'suggestion.html'
    form_class = SuggestionForm
    success_url = reverse_lazy('suggestion')  

    def form_valid(self, form):
        suggestion = form.save(commit=False)
        if self.request.user.is_authenticated:
            suggestion.user = self.request.user
        suggestion.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['suggestions'] = Suggestion.objects.select_related('user').order_by('-created_at')
        return context
    

class ConversationList(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Conversation.objects.all()
        else:
            return Conversation.objects.filter(user=user)


class HelpChat(LoginRequiredMixin, FormView, DetailView):
    template_name = 'help_chat.html'
    model = Conversation
    form_class = HelpMessageForm
    context_object_name = 'conversation'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    def get_success_url(self):
        return reverse_lazy('conversation_detail', kwargs={'pk': self.get_object().pk})

    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.sender = self.request.user
        msg.conversation = self.get_object()
        if self.request.user.is_superuser:
            msg.recipient = self.get_object().user
        else:
            msg.recipient = None
        msg.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.get_object().messages.order_by('created_at')
        return context


class RedirectToConversation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return redirect('conversation_list')
        else:
            conversation, created = Conversation.objects.get_or_create(user=user)
            return redirect('conversation_detail', pk=conversation.pk)
        

def custom_error_view(request, exception=None, status_code=500, message="Ha ocurrido un error"):
    context = {
        "status_code": status_code,
        "message": message
    }
    return render(request, "error.html", context=context, status=status_code)

def error_404_view(request, exception):
    return custom_error_view(request, exception, 404, "La página que buscas no fue encontrada.")

def error_500_view(request):
    return custom_error_view(request, status_code=500, message="Error interno del servidor.")

def error_403_view(request, exception):
    return custom_error_view(request, exception, 403, "Acceso denegado.")

def error_400_view(request, exception):
    return custom_error_view(request, exception, 400, "Solicitud incorrecta.")
