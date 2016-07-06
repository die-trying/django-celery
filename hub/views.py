from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from moneyed import Money

from hub.models import Class
from lessons.models import OrdinaryLesson


@login_required
def single(request):
    c = Class(
        customer=request.user.crm,
        lesson=OrdinaryLesson.get_default(),
        buy_price=Money(10, 'USD'),
    )
    c.save()
    return redirect('/')
