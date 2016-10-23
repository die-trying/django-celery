from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/hours.json$', views.hours, name='hours'),
    url(r'(?P<username>.+)/', views.TeacherDetail.as_view()),
]
