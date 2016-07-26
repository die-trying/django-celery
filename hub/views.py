import iso8601
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from moneyed import Money

from hub.models import Class, Subscription
from lessons.models import OrdinaryLesson
from products.models import Product1
from teachers.models import Teacher


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

    lesson_type = get_object_or_404(ContentType, app_label='lessons', pk=type_id)

    found = Class.objects.find_class(
        customer=request.user.crm,
        lesson_type=lesson_type
    )
    if not found['result']:
        if just_checking:
            del found['class']
            return JsonResponse(found, safe=True)
        else:
            return Http404(found['text'])

    found['class'].schedule(
        teacher=get_object_or_404(Teacher, pk=teacher),
        date=iso8601.parse_date('%s %s' % (date, time))
    )

    if just_checking:
        del found['class']
        return JsonResponse(found, safe=True)

    found['class'].save()
    return redirect('/')  # TODO: a page with success story
