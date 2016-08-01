from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<date>[\d\-]+)/type/(?P<lesson_type>\d+)/teachers.json$', views.teachers, name='teachers'),
    url(r'(?P<date>[\d\-]+)/type/(?P<lesson_type>\d+)/lessons.json$', views.lessons, name='lessons'),

    url(r'(?P<username>.+)/hours.json$', views.hours, name='hours'),
]
