from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/(?P<date>.+)/slots.json$', views.teacher_slots_json, name='teacher_slots_json'),
    url(r'(?P<date>.+)/slots.json$', views.all_slots_json, name='slots_json'),
    url(r'(?P<username>.+)/hours.json$', views.teacher_hours_json, name='teacher_hours_json'),
]
