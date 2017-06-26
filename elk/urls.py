from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from acc.views import Homepage
from teachers.api.viewsets import TeacherViewSet
from timeline.api.viewsets import TimelineViewset

"""
URL of every app should be namespaced with the prefix of the app name,
in example namespace for buy_single url in the market app is market:buy_single,
and for starting social auth — app:social:begin.
"""


api_router = DefaultRouter()
api_router.register(r'teachers', TeacherViewSet)
api_router.register(r'timeline', TimelineViewset)

urlpatterns = [
    url(name='home', regex=r'^$', view=Homepage.as_view()),

    url(r'^accounts/', include('acc.urls', namespace='acc')),
    url(r'^crm/', include('crm.urls', namespace='crm')),
    url(r'^market/', include('market.urls', namespace='market')),
    url(r'^timeline/', include('timeline.urls', namespace='timeline')),
    url(r'^teachers/', include('teachers.urls', namespace='teachers')),
    url(r'^payments/', include('payments.urls', namespace='payments')),

    url(r'^api/', include(api_router.urls, namespace='api')),
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
