from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView

from elk.views import DeleteWithoutConfirmationView, StaffRequiredDetailView, StaffRequiredTemplateView
from market.auto_schedule import AutoSchedule
from market.sortinghat import SortingHat
from timeline.forms import EntryForm as TimelineEntryForm
from timeline.models import Entry as TimelineEntry


class TeacherCalendar(StaffRequiredTemplateView):
    template_name = 'timeline/calendar.html'

    def get_context_data(self, **kwargs):
        Teacher = apps.get_model('teachers.Teacher')
        teacher_username = kwargs['username']
        return {
            'object': get_object_or_404(Teacher, user__username=teacher_username),
            'others': Teacher.objects.exclude(user__username=teacher_username)
        }


class TimelineEntryBaseView():
    model = TimelineEntry
    form_class = TimelineEntryForm
    template_name = 'timeline/entry_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Teacher = apps.get_model('teachers.Teacher')
        context['teacher'] = get_object_or_404(Teacher, user__username=self.kwargs['username'])
        return context

    def get_success_url(self):
        return reverse(
            'timeline:timeline',
            kwargs={'username': self.kwargs['username']}
        )

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class EntryCreate(TimelineEntryBaseView, CreateView):
    pass


class EntryUpdate(TimelineEntryBaseView, UpdateView):
    pass


class EntryDelete(TimelineEntryBaseView, DeleteWithoutConfirmationView):
    pass


class TimelineEntryCardView(StaffRequiredDetailView):
    """
    Get timeline entry card by pk.
    """
    template_name = 'timeline/entry/card.html'
    model = TimelineEntry

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        Class = apps.get_model('market.Class')
        ctx['students_for_adding'] = Class.objects \
            .find_student_classes(lesson_type=self.object.lesson_type) \
            .exclude(customer__pk__in=self.object.classes.distinct('customer__pk'))

        return ctx


@staff_member_required
def delete_customer(request, username, pk, customer):
    Class = apps.get_model('market.Class')
    c = get_object_or_404(Class, timeline__id=pk, timeline__teacher__user__username=username, customer__pk=customer)
    entry = c.timeline
    c.delete()

    try:
        entry.refresh_from_db()
    except TimelineEntry.DoesNotExist:
        return redirect(reverse('timeline:timeline', kwargs={'username': username}))

    return redirect(reverse('timeline:entry_card', kwargs={'username': username, 'pk': pk}))


@staff_member_required
def add_customer(request, username, pk, customer):
    """
    Add customer to a particular timeline entry

    This view feeds the SortingHat with exact parameters from particular entry,
    hoping that the hat will find the same entry, as requested. If you will find
    problems with it, the probable solution would be adding a timeline_entry as
    an input parameter to the SortingHat.
    """
    entry = get_object_or_404(TimelineEntry, teacher__user__username=username, pk=pk)

    start = timezone.localtime(entry.start)

    Customer = apps.get_model('crm.Customer')

    hat = SortingHat(
        customer=get_object_or_404(Customer, pk=customer),
        lesson_type=entry.lesson_type.pk,
        teacher=entry.teacher,
        date=format(start, 'Y-m-d'),
        time=format(start, 'H:i'),
    )

    if not hat.do_the_thing():
        raise Http404('%s: %s' % (hat.err, hat.msg))

    hat.c.save()
    return redirect(reverse('timeline:entry_card', kwargs={'username': username, 'pk': hat.c.timeline.pk}))


@staff_member_required
def check_entry(request, username, start, end):
    """
    Check timeline entry for validity.

    Typicaly used when creating a timeline entry by-hand at /timeline/
    TODO: move it to the API
    """
    start = timezone.make_aware(parse_datetime(start))
    end = timezone.make_aware(parse_datetime(end))

    Teacher = apps.get_model('teachers.Teacher')

    s = AutoSchedule(
        teacher=get_object_or_404(Teacher, user__username=username)
    )

    try:
        s.clean(start, end)

    except ValidationError as e:
        return JsonResponse({'result': e.__class__.__name__})

    return JsonResponse({'result': 'ok'})
