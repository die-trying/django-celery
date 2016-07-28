from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from moneyed import Money

from hub.models import Class, Subscription
from lessons.models import OrdinaryLesson
from products.models import Product1
from teachers.models import Teacher
from timeline.models import Entry as TimelineEntry


@login_required
def single(request):
    c = Class(
        customer=request.user.crm,
        lesson=OrdinaryLesson.get_default(),
        buy_price=Money(10, 'USD'),
    )
    c.request = request
    c.save()
    return redirect('/')


@login_required
def subscription(request):
    s = Subscription(
        customer=request.user.crm,
        product=Product1.objects.get(pk=1),
        buy_price=Money(150, 'USD')
    )
    s.request = request
    s.save()
    return redirect('/')


@login_required
def step1(request):
    return render(request, 'hub/schedule_popup/schedule_popup.html')


@login_required
def step2_by_type(request, teacher, type_id, date, time):
    just_checking = False
    if 'check' in request.GET.keys():
        just_checking = True

    result = Class.objects.try_to_schedule(
        teacher=get_object_or_404(Teacher, pk=teacher),
        lesson_type=get_object_or_404(ContentType, app_label='lessons', pk=type_id),
        date=parse_datetime(date + ' ' + time)
    )

    if just_checking:
        del result['c']
        return JsonResponse(result, safe=True)

    if not result['result']:
        return Http404('%s: %s' % (result['error'], result['text']))

    result['c'].save()

    return redirect('/')  # TODO: a page with success story


@login_required
def step2_by_entry(request, teacher, entry_id):
    just_checking = False
    if 'check' in request.GET.keys():
        just_checking = True

    result = Class.objects.try_to_schedule(
        teacher=get_object_or_404(Teacher, pk=teacher),
        entry=get_object_or_404(TimelineEntry, pk=entry_id),
    )

    if just_checking:
        del result['c']
        return JsonResponse(result, safe=True)

    if not result['result']:
        return Http404('%s: %s' % (result['error'], result['text']))

    result['c'].save()
    return redirect('/')  # TODO: a page with success story
