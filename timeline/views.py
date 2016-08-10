from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from django.views.generic.edit import CreateView, UpdateView

from elk.utils import date
from teachers.models import Teacher
from timeline.forms import EntryForm as TimelineEntryForm
from timeline.models import Entry as TimelineEntry


@staff_member_required
def calendar(request, username):
    return render(request, 'timeline/calendar/user.html', context={
        'object': get_object_or_404(Teacher, user__username=username),
        'others': Teacher.objects.exclude(user__username=username).order_by('user__last_name'),
    })


class TeacherCtxMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = get_object_or_404(Teacher, user__username=self.kwargs['username'])
        return context


class calendar_create(TeacherCtxMixin, CreateView):
    template_name = 'timeline/forms/entry/create.html'
    form_class = TimelineEntryForm

    def get_success_url(self):
        return reverse('timeline:timeline', kwargs=self.kwargs)


class calendar_update(TeacherCtxMixin, UpdateView):
    template_name = 'timeline/forms/entry/update.html'
    form_class = TimelineEntryForm
    model = TimelineEntry

    def get_success_url(self):
        return reverse('timeline:timeline',
                       kwargs={'username': self.kwargs['username']},
                       )


@staff_member_required
def calendar_delete(request, username, pk):
    teacher = get_object_or_404(Teacher, user__username=username)
    entry = get_object_or_404(TimelineEntry, teacher=teacher, pk=pk)
    entry.delete()
    return redirect(reverse('timeline:timeline', kwargs={'username': username}))


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
    entry = TimelineEntry(
        start=parse_datetime(start),
        end=parse_datetime(end),
        teacher=get_object_or_404(Teacher, user__username=username),
    )
    return JsonResponse({
        'is_overlapping': entry.is_overlapping(),
        'is_fitting_hours': entry.is_fitting_working_hours(),
    }, safe=False)
