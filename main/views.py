from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView  
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, ContactForm, SuggestionForm, HelpMessageForm
from .models import Anime, User, Episode, Comment, Conversation, Suggestion
from .utils.recaptcha import verify_recaptcha

# Vista del mapa del sitio
class SiteMapView(TemplateView):  
    template_name = 'sitemap.html'  


# Vista de inicio de sesión
class Login(LoginView):
    model = User
    fields = '__all__'
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
          messages.success(self.request, "¡Has iniciado sesión exitosamente!")
          return super().form_valid(form)

    # Si el inicio de sesión es correcto, te redirige al index
    def get_success_url(self):
        return reverse_lazy('anime_list')


# Vista de registro 
class Signup(FormView):
    template_name = 'signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('anime_list')

    # Verifica el reCAPTCHA antes de guardar el formulario
    def form_valid(self, form):
        token = self.request.POST.get("g-recaptcha-response")
        if not token or not verify_recaptcha(token):
            messages.error(self.request, "Error de reCAPTCHA. Intenta de nuevo.")
            return self.form_invalid(form)

        user = form.save()
        if user is not None:
            login(self.request, user)

        messages.success(self.request, "¡Te has registrado exitosamente!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RECAPTCHA_SITE_KEY'] = settings.RECAPTCHA_SITE_KEY
        return context
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('anime_list')
        return super(Signup, self).get(*args, **kwargs)
    

# Vista para actualizar el perfil del usuario
class Profile(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['icon']   
    template_name = 'profile.html'
    success_url = reverse_lazy('anime_list')


# Vista para mostrar los animes en el index
class AnimeList(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'index.html'


# Vista para hacer busquedas de los animes
class SearchBar(ListView):
    model = Anime
    context_object_name = 'animes'
    template_name = 'search.html'

    # Hace la búsqueda de los animes
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self.request.GET.get('search') or ''

        if search_value:
            context['animes'] = context['animes'].filter(title__icontains=search_value)
        context['search_value'] = search_value
        return context


# Vista de ayuda
class Help(View):
    def get(self, request):
        return render(request, 'help.html') 


# Vista para mostrar a detalle el anime seleccionado y sus episodios
class AnimeDetail(LoginRequiredMixin, DetailView):
    model = Anime
    context_object_name = 'anime'
    template_name = 'anime_detail.html'
    
    # Muestra los capítulos del anime seleccionado
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['episodes'] = Episode.objects.filter(anime=self.object).order_by('episode_number')
        return context


# Vista para mostrar y poder ver el capitulo seleccionado del anime y comentarios
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
    
    # Maneja el envio de comentarios en el capitulo
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        content = request.POST.get('content')

        if request.user.is_authenticated and content:
            Comment.objects.create(user=request.user, anime=self.object.anime, episode=self.object, content=content)
        return HttpResponseRedirect(self.request.path_info)
    

# Vista de contacto
class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact') 

    # Maneja el envio del formulario de contacto
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
        messages.success(self.request, "¡Correo enviado, te responderemos lo mas pronto posible!")
        return super().form_valid(form)


# Vista de Buzón de sugerencias
class SuggestionView(LoginRequiredMixin, FormView):
    template_name = 'suggestion.html'
    form_class = SuggestionForm
    success_url = reverse_lazy('suggestion')  

    # Maneja el envio del formulario de sugerencias
    def form_valid(self, form):
        suggestion = form.save(commit=False)
        if self.request.user.is_authenticated:
            suggestion.user = self.request.user
        suggestion.save()
        messages.success(self.request, "¡Sugerencia enviada!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['suggestions'] = Suggestion.objects.select_related('user').order_by('-created_at')
        return context


# Vista del chat
class ConversationList(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'conversation_list.html'
    context_object_name = 'conversations'

    # Obtiene la conversacion del usuario o todas las conversaciones si es administrador
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Conversation.objects.all()
        else:
            return Conversation.objects.filter(user=user)


# Vista del chat de ayuda
class HelpChat(LoginRequiredMixin, FormView, DetailView):
    template_name = 'help_chat.html'
    model = Conversation
    form_class = HelpMessageForm
    context_object_name = 'conversation'

    # Obtiene el objeto de la conversación, asegurando que el usuario tenga permiso para acceder a ella
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.user != self.request.user:
            raise PermissionDenied()
        return obj

    # Redirige a la conversación específica después de enviar un mensaje
    def get_success_url(self):
        return reverse_lazy('conversation_detail', kwargs={'pk': self.get_object().pk})
    
    # Maneja el envio del formulario de mensajes en la conversación
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
    
    # Muestra los mensajes de la conversación
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = self.get_object().messages.order_by('created_at')
        return context


# Vista para redirigir al usuario a su conversación o a la lista de conversaciones si es administrador
class RedirectToConversation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return redirect('conversation_list')
        else:
            conversation, created = Conversation.objects.get_or_create(user=user)
            return redirect('conversation_detail', pk=conversation.pk)
        

# Manejo de errores personalizados
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