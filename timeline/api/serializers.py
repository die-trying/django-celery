from rest_framework import serializers

from timeline.models import Entry as TimelineEntry


class TimelineEntrySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEntry
        fields = ('id', 'title', 'teacher', 'start', 'end', 'is_free', 'taken_slots', 'slots')

    def get_title(self, obj):
        return str(obj)


class TimelineEntryCustomerSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEntry
        fields = [
            'id',
            'title',
            'teacher',
            'start',
            'taken_slots',
            'slots'
        ]

    def get_title(self, obj):
        return str(obj.event_title())
