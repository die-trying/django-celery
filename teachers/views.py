from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from teachers.models import Teacher, WorkingHours


@staff_member_required
def hours(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)

    hours_list = []

    for hours in get_list_or_404(WorkingHours, teacher=teacher):
        hours_list.append(hours.as_dict())

    return JsonResponse(hours_list, safe=False)


class TeacherDetail(DetailView):
    model = Teacher
    slug_url_kwarg = 'username'
    slug_field = 'user__username'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['timeslots'] = list(
            ctx['object'].free_slots_for_dates(self.request.user.crm.classes.dates_for_planning())
        )

        return ctx
