from django import forms
from main.models import User, Suggestion, HelpMessage

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'minlength': 8}))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(attrs={'minlength': 8}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nombre")
    email = forms.EmailField(label="Correo electrónico")
    subject = forms.CharField(max_length=150, required=False, label="Asunto")
    message = forms.CharField(widget=forms.Textarea, label="Mensaje")

    
class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['subject','message']


class HelpMessageForm(forms.ModelForm):
    class Meta:
        model = HelpMessage
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'placeholder': 'Escribe algo....',})}