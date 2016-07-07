from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from hub.models import Class, Subscription
from lessons.models import OrdinaryLesson
from moneyed import Money
from products.models import Product1


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
