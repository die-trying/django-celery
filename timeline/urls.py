from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/calendar.json', views.calendar_json, name='calendar.json'),
]
