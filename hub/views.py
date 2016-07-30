from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from moneyed import Money

from hub.models import Class, Subscription
from hub.scheduler import SortingHat
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
def step2(request, teacher, type_id, date, time):
    hat = SortingHat(
        customer=request.user.crm,
        teacher=get_object_or_404(Teacher, pk=teacher),
        lesson_type=type_id,
        date=date,
        time=time,
    )

    hat.do_the_thing()  # do the actual scheduling

    if 'check' in request.GET.keys():
        return JsonResponse({
            'result': hat.result,
            'error': hat.err,
            'text': hat.msg,
        })

    if not hat.result:
        return Http404('%s: %s' % (hat.err, hat.text))

    hat.c.save()  # save a hat-generated class
    return redirect('/')  # TODO: a page with success story
