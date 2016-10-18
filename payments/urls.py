from django.conf.urls import url

from payments import views

urlpatterns = [
    url(r'process/', views.process, name='process'),
    url(r'(?P<product_type>\d+)/(?P<product_id>\d+)/success/', views.success, name='success'),
    url(r'(?P<product_type>\d+)/(?P<product_id>\d+)/failure/', views.failure, name='failure'),
]
