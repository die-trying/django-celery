from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+).json', views.calendar_json, name='calendar.json'),
    url(r'(?P<username>.+)/', views.calendar, name='calendar'),
]
