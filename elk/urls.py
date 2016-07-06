from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

"""
URL of every app should be namespaced with the prefix of the app name,
in example namespace for buy_single url in the hub app is hub:buy_single,
and for starting social auth — app:social:begin.
"""

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='index.html'))),

    url(r'^accounts/', include('acc.urls', namespace='acc')),
    url(r'^hub/', include('hub.urls', namespace='hub')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^markdown/', include('django_markdown.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
