from rest_framework import serializers

from elk.api.fields import MarkdownField


class LessonSerializer(serializers.ModelSerializer):
    announce = MarkdownField()
    description = MarkdownField()

    class Meta:
        fields = ('id', 'name', 'announce', 'description', 'duration')


class HostedLessonSerializer(LessonSerializer):
    host = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'host', 'announce', 'description', 'duration')

    def get_host(self, obj):
        return obj.host.user.crm.full_name


def factory(m):
    """
    Returns a serializer for any lesson
    """
    if hasattr(m, 'host'):
        Super = HostedLessonSerializer
    else:
        Super = LessonSerializer

    class GeneratedSerializer(Super):
        class Meta(Super.Meta):
            model = m.__class__

    return GeneratedSerializer
