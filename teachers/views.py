from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404

from teachers.models import Teacher, WorkingHours


@staff_member_required
def hours(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)

    hours_list = []

    for hours in get_list_or_404(WorkingHours, teacher=teacher):
        hours_list.append(hours.as_dict())

    return JsonResponse(hours_list, safe=False)
