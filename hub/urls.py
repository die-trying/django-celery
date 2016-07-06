from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'/buy-single', views.single, name='single')
]
