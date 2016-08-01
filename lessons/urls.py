from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/available.json$', views.available_lessons, name='available'),
]
