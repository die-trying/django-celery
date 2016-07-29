from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from elk.utils import date
from teachers.models import Teacher
from timeline.forms import EntryForm as TimelineEntryForm
from timeline.models import Entry as TimelineEntry


@staff_member_required
def calendar(request, username):
    return render(request, 'timeline/calendar/user.html', context={
        'object': get_object_or_404(Teacher, user__username=username)
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


class schedule_step01(TemplateView):
    template_name = 'timeline/schedule/step_01.html'


@staff_member_required
def calendar_delete(request, username, pk):
    teacher = get_object_or_404(Teacher, user__username=username)
    entry = get_object_or_404(TimelineEntry, teacher=teacher, pk=pk)
    entry.active = 0
    entry.save()
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
def check_overlap(request, username):
    teacher = get_object_or_404(Teacher, user__username=username)

    entry = TimelineEntry()
    entry_id = request.GET.get('entry')
    if entry_id:
        entry = get_object_or_404(TimelineEntry, pk=entry_id)
    else:
        entry.start = parse_datetime(request.GET.get('start'))
        entry.end = parse_datetime(request.GET.get('end'))
        entry.teacher = teacher

    return JsonResponse(entry.is_overlapping(), safe=False)
