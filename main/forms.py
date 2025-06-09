from django import forms
from main.models import User, Suggestion, HelpMessage
from django.contrib.auth.password_validation import validate_password
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'minlength': 8}))
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(attrs={'minlength': 8}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password(password1)
        return password1

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

    
class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['subject','message']


class HelpMessageForm(forms.ModelForm):
    class Meta:
        model = HelpMessage
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'placeholder': 'Escribe algo....',})}