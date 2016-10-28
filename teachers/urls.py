from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/', views.TeacherDetail.as_view()),
]
