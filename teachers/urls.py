from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/hours.json$', views.hours_json, name='hours_json'),
]
