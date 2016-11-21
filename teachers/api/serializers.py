from django.template.defaultfilters import time
from django.utils import timezone
from rest_framework import serializers

from teachers.models import Teacher


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    teacher_photo = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ('id', 'name', 'announce', 'profile_photo', 'teacher_photo')
        depth = 2

    def get_name(self, obj):
        return obj.user.crm.full_name

    def get_profile_photo(self, obj):
        return obj.get_teacher_avatar()

    def get_teacher_photo(self, obj):
        return obj.get_teacher_photo()


class TimeSlotSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'server': time(timezone.localtime(obj), 'H:i'),
            'user': time(timezone.localtime(obj), 'TIME_FORMAT'),
        }
