from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404

from elk.utils.filters import request_filters
from teachers.models import Teacher, WorkingHours
from timeline.models import ALLOWED_TIMELINE_FILTERS


@staff_member_required
def teacher_hours(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)

    hours_list = []

    for hours in get_list_or_404(WorkingHours, teacher=teacher):
        hours_list.append(hours.as_dict())

    return JsonResponse(hours_list, safe=False)


@login_required
def slots_by_teacher(request, username, date):
    """
    Get free time slots for a particular teacher. The used method is
    :model:`teachers.Teacher`.find_free_slots, filtering is done via
    :model:`timeline.Entry`.
    """
    teacher = get_object_or_404(Teacher, user__username=username)

    kwargs = request_filters(request, ALLOWED_TIMELINE_FILTERS)

    slots = teacher.find_free_slots(date=date, **kwargs)

    if not slots:
        raise Http404('No slots found')

    return JsonResponse(slots.as_dict(), safe=False)


@login_required
def slots_by_date(request, date):
    """
    Return of JSON of time slots, avaialbe for planning. The used method is
    :model:`teachers.Teacher`.find_free, filtering is done via :model:`timeline.Entry`.
    """
    kwargs = request_filters(request, ALLOWED_TIMELINE_FILTERS)

    teachers_with_slots = Teacher.objects.find_free(date=date, **kwargs)
    if not teachers_with_slots:
        raise Http404('No free teachers found')

    teachers = []
    for teacher in teachers_with_slots:
        teacher_dict = teacher.as_dict()
        teacher_dict['slots'] = teacher.free_slots.as_dict()
        teachers.append(teacher_dict)

    return JsonResponse(teachers, safe=False)
