import django_filters
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from elk.api.permissions import StaffMemberRequiredPermission
from timeline.api.serializers import TimelineEntryCustomerSerializer, TimelineEntrySerializer
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

    permission_classes = [StaffMemberRequiredPermission]

    @detail_route(methods=['GET'], permission_classes=[IsAuthenticated])
    def schedule_check(self, request, pk=None):
        entry = self.get_object()
        serializer = TimelineEntryCustomerSerializer(entry)
        return Response(data=serializer.data)
