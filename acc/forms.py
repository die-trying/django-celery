from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(  # In Django 1.10 you should use `UsernameField` instead of this
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': ''
        }),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }),
    )
    pass
