from django.conf.urls import url

from payments.views import process

urlpatterns = [
    url(r'process', process, name='process'),
]
