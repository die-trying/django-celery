from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

"""
URL of every app should be namespaced with the prefix of the app name,
in example namespace for buy_single url in the market app is market:buy_single,
and for starting social auth — app:social:begin.
"""

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='acc/index.html'))),

    url(r'^accounts/', include('acc.urls', namespace='acc')),
    url(r'^market/', include('market.urls', namespace='market')),
    url(r'^history/', include('history.urls', namespace='history')),
    url(r'^timeline/', include('timeline.urls', namespace='timeline')),
    url(r'^lessons/', include('lessons.urls', namespace='lessons')),
    url(r'^teachers/', include('teachers.urls', namespace='teachers')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^markdown/', include('django_markdown.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
