from django import template
from django.conf import settings
from django.template import Context
from django.template.loader import get_template

from payments.stripe import stripe_amount

register = template.Library()


@register.simple_tag(takes_context=True)
def stripe_form(context, *args, **kwargs):
    tpl = get_template('payments/_stripe.html')

    ctx = _ctx(*args, **kwargs)
    ctx['csrf_token'] = context.get('csrf_token')

    return tpl.render(Context(ctx))


def _ctx(product, cost, crm):
    return {
        'stripe_pk': settings.STRIPE_PK,
        'amount': int(stripe_amount(cost)),
        'currency': str(cost.currency),
        'product': product,
        'crm': crm,
    }
