# dashboard/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'department', 'password1', 'password2')
