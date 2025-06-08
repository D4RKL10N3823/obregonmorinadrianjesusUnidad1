from django import forms
from .models import User, Suggestion, HelpMessage, User

class CustomUserCreationForm(forms.ModelForm):
    # Creación de campos adicionales para la contraseña con validación de longitud de 8 caracteres minimos
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'minlength': 8}))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(attrs={'minlength': 8}))

    class Meta:
        model = User
        fields = ['username', 'email']

    #Funcion para verificar que el correo no se repita
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email
    
    # Funcion para validar que las contraseñas sean iguales
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    # Guarda la contraseña hasheada
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  
        if commit:
            user.save()
        return user
    

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['name', 'message']


class HelpMessageForm(forms.ModelForm):
    class Meta:
        model = HelpMessage
        fields = ['message']  