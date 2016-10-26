from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView

from crm.models import Customer
from elk.utils import date
from elk.views import DelteWithoutConfirmationView
from market.auto_schedule import AutoSchedule
from market.models import Class
from market.sortinghat import SortingHat
from teachers.models import Teacher
from timeline.forms import EntryForm as TimelineEntryForm
from timeline.models import Entry as TimelineEntry


@staff_member_required
def calendar(request, username):
    return render(request, 'timeline/calendar/user.html', context={
        'object': get_object_or_404(Teacher, user__username=username),
        'others': Teacher.objects.exclude(user__username=username).order_by('user__last_name'),
    })


class TimelineEntryBaseView():
    model = TimelineEntry
    form_class = TimelineEntryForm
    template_name = 'timeline/entry_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class EntryDelete(TimelineEntryBaseView, DelteWithoutConfirmationView):
    pass


@staff_member_required
def entry_card(request, username, pk):
    entry = get_object_or_404(TimelineEntry, teacher__user__username=username, pk=pk)
    return render(request, 'timeline/entry/card.html', context={
        'object': entry,
        'students_for_adding': Class.objects.find_student_classes(lesson_type=entry.lesson_type).exclude(customer__pk__in=entry.classes.distinct('customer__pk'))
    })


@staff_member_required
def delete_customer(request, username, pk, customer):
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
def calendar_json(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)
    entries = []
    start = request.GET.get('start', date.ago(days=16))
    end = request.GET.get('end', date.fwd(days=16))

    for entry in get_list_or_404(TimelineEntry,
                                 start__range=(start, end),
                                 teacher=teacher,
                                 ):
        entries.append(entry.as_dict())

    return JsonResponse(entries, safe=False)


@staff_member_required
def check_entry(request, username, start, end):
    start = timezone.make_aware(parse_datetime(start))
    end = timezone.make_aware(parse_datetime(end))

    s = AutoSchedule(
        teacher=get_object_or_404(Teacher, user__username=username)
    )

    try:
        s.clean(start, end)

    except ValidationError as e:
        return JsonResponse({'result': e.__class__.__name__})

    return JsonResponse({'result': 'ok'})
