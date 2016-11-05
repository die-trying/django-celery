from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from lessons.api.serializers import factory as lesson_serializer_factory
from teachers.api.serializers import TeacherSerializer
from teachers.models import Teacher


class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @detail_route(methods=['GET'])
    def available_lessons(self, request, pk=None, format=None):
        teacher = self.get_object()
        lesson_type = get_object_or_404(ContentType, pk=request.GET['lesson_type'])

        available_lessons = []
        for lesson in teacher.available_lessons(lesson_type):
            Serializer = lesson_serializer_factory(lesson)
            available_lessons.append(
                Serializer(lesson).data
            )

        return Response(available_lessons)
