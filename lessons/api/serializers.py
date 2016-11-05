from rest_framework import serializers

from elk.api.fields import MarkdownField


class LessonSerializer(serializers.ModelSerializer):
    announce = MarkdownField()
    description = MarkdownField()

    class Meta:
        fields = ('id', 'name', 'announce', 'description', 'duration')


class HostedLessonSerializer(LessonSerializer):
    host = serializers.SerializerMethodField()
    host_id = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'host', 'host_id', 'profile_photo', 'announce', 'description', 'duration')

    def get_host(self, obj):
        return obj.host.user.crm.full_name

    def get_profile_photo(self, obj):
        return obj.host.user.crm.get_profile_photo()

    def get_host_id(self, obj):
        return obj.host.id


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
