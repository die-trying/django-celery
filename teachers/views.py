from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404

from teachers.models import WorkingHours


@staff_member_required
def hours_json(request, username):
    user = get_object_or_404(User, username=username)

    hours_list = []

    for hours in get_list_or_404(WorkingHours, teacher=user.teacher_data):
        hours_list.append(hours.as_dict())

    return JsonResponse(hours_list, safe=False)
