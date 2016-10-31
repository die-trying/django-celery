from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<username>.+)/', views.TeacherDetail.as_view(), name='detail'),
    url(r'$', views.TeacherList.as_view(), name='list')
]
