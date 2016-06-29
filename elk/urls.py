from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import admin

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),

    url(r'^accounts/', include('acc.urls')),

    url(r'^secret.html$', login_required(TemplateView.as_view(template_name='secret.html')), name='secret'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^markdown/', include('django_markdown.urls')),
]
