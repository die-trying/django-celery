from django.conf.urls import url
# from django.views.generic import TemplateView

import django.contrib.auth.views as stock_views

from . import forms

urlpatterns = [
    url(r'^login/$', stock_views.login, {'authentication_form': forms.AuthenticationForm}, name='login')
]
