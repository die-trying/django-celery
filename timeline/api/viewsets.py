import django_filters
from rest_framework import viewsets

from timeline.api.serializers import TimelineEntrySerializer
from timeline.models import Entry as TimelineEntry


class TimelineFilter(django_filters.rest_framework.FilterSet):
    teacher = django_filters.NumberFilter(name='teacher__id')
    start = django_filters.DateFromToRangeFilter()

    class Meta:
        model = TimelineEntry
        fields = ['teacher', 'start']


class TimelineViewset(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEntry.objects.all().prefetch_related('lesson').order_by('start')
    serializer_class = TimelineEntrySerializer

    filter_class = TimelineFilter
