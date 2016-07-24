from django.contrib.auth.decorators import login_required
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
def step01(request):
    return render(request, 'hub/schedule_popup/schedule_popup.html')


@login_required
def step02_by_type(request, teacher, id, date, time):
    teacher = get_object_or_404(Teacher, pk=teacher)
    return render(request, 'hub/schedule_popup/step_02.html')
