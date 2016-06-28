from django.conf.urls import url

import django.contrib.auth.views as stock_views

from . import forms

urlpatterns = [
    url(r'^login/$', stock_views.login, {'authentication_form': forms.AuthenticationForm}, name='login'),
    url(r'^logout/$', stock_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password_change/$', stock_views.password_change, name='password_change'),
    url(r'^password_change/done/$', stock_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', stock_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', stock_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        stock_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', stock_views.password_reset_complete, name='password_reset_complete'),
]
