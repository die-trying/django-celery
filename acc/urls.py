from django.conf.urls import url, include

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
    url('', include('social.apps.django_app.urls', namespace='social'))
]
