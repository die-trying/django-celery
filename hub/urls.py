from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^buy-single$', views.single, name='buy_a_single')
]
