from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/create/$', views.calendar_create.as_view(), name='timeline_create'),
    url(r'(?P<username>.+)/available_lessons.json$', views.available_lessons_json, name='available_lessons_json'),
    url(r'(?P<username>.+).json', views.calendar_json, name='timeline.json'),
    url(r'(?P<username>.+)/$', views.calendar, name='timeline'),
]
