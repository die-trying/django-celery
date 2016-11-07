from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template import Context
from django.template.loader import get_template

from payments.stripe import stripe_amount, stripe_currency

register = template.Library()


@register.simple_tag(takes_context=True)
def stripe_form(context, caption, classes, *args, **kwargs):
    tpl = get_template('payments/_partial/stripe.html')

    ctx = _ctx(*args, **kwargs)
    ctx['csrf_token'] = context.get('csrf_token')

    ctx['caption'] = caption
    ctx['classes'] = classes

    return tpl.render(Context(ctx))


@register.simple_tag
def stripe_processing_popup():
    tpl = get_template('payments/_partial/processing-popup.html')
    return tpl.render(Context({}))


def _ctx(product, cost, crm):
    return {
        'stripe_pk': settings.STRIPE_PK,
        'amount': str(cost.amount),
        'stripe_amount': stripe_amount(cost),
        'currency': stripe_currency(cost),
        'product': product,
        'product_type': ContentType.objects.get_for_model(product).pk,
        'crm': crm,
    }
