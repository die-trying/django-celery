from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<date>[\d\-]+)/type/(?P<lesson_type>\d+)/slots.json$', views.slots_by_type, name='type_slots'),
    url(r'(?P<username>.+)/available.json$', views.available_lessons, name='available'),
]
