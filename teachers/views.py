from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404

from teachers.models import Teacher, WorkingHours


@staff_member_required
def hours(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)

    hours_list = []

    for hours in get_list_or_404(WorkingHours, teacher=teacher):
        hours_list.append(hours.as_dict())

    return JsonResponse(hours_list, safe=False)


@login_required
def teachers(request, date, lesson_type):
    """
    Return of JSON of time slots, avaialbe for planning. The used method is
    :model:`teachers.Teacher`.find_free, filtering is done via :model:`timeline.Entry`.
    """
    teachers_with_slots = Teacher.objects.find_free(date=date, lesson_type=lesson_type)
    if not teachers_with_slots:
        raise Http404('No free teachers found')

    teachers = []
    for teacher in teachers_with_slots:
        teacher_dict = teacher.as_dict()
        teacher_dict['slots'] = teacher.free_slots.as_dict()
        teachers.append(teacher_dict)

    return JsonResponse(teachers, safe=False)


@login_required
def lessons(request, date, lesson_type):
    """
    Return a JSON of avaialble time slots for distinct date and lesson_type
    """
    lessons = Teacher.objects.find_lessons(date=date, lesson_type=lesson_type)
    if not lessons:
        raise Http404('No lessons found on this date')

    result = []
    for lesson in lessons:
        lesson_dict = lesson.as_dict()
        lesson_dict['slots'] = lesson.free_slots.as_dict()
        result.append(lesson_dict)

    return JsonResponse(result, safe=False)
