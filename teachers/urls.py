from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<date>[\d\-]+)/slots.json$', views.slots_by_date, name='slots_by_date'),
    url(r'(?P<username>.+)/(?P<date>[\d\-]+)/slots.json$', views.slots_by_teacher, name='slots_by_teacher'),

    url(r'(?P<username>.+)/hours.json$', views.teacher_hours, name='teacher_hours'),
]
