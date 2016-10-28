from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from elk.views import JSONDetailView
from teachers.models import Teacher


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


class TeacherJSONDetail(JSONDetailView, TeacherDetail):
    def serialize(self, context):
        context['object'] = context['object'].as_dict()
        context['timeslots'] = ''
        return context
