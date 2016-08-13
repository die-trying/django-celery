from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/type/(?P<lesson_type>\d+)/available.json$', views.available_lessons, name='available'),
]
