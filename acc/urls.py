from django.conf.urls import include, url

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
