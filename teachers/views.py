from elk.views import LoginRequiredDetailView, LoginRequiredListView
from teachers.models import Teacher


class TeacherDetail(LoginRequiredDetailView):
    model = Teacher
    slug_url_kwarg = 'username'
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['timeslots'] = list(
            ctx['object'].free_slots_for_dates(self.request.user.crm.classes.dates_for_planning())
        )

        return ctx


class TeacherList(LoginRequiredListView):
    model = Teacher
    queryset = Teacher.objects.with_photos()
