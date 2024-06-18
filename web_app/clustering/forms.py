from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label="Username")
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Password")


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


# Formulaire de mofification du compte
class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = ('username','email', 'first_name', 'last_name','password')


class UploadFileForm(forms.Form):
    title=forms.CharField(max_length=50)
    file=forms.FileField()

    