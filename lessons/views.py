from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from teachers.models import Teacher


@staff_member_required
def available_lessons(request, username, lesson_type):
    teacher = get_object_or_404(Teacher, user__username=username)
    lesson_type = int(lesson_type)
    lessons = [i.as_dict() for i in teacher.available_lessons(lesson_type)]
    return JsonResponse(lessons, safe=False)
