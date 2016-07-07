from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url('^(calendar/P<username>.+)/$', views.calendar, name='calendar'),
    url(r'^calendar/(?P<username>.+).json', views.calendar_json, name='calendar.json'),
]
