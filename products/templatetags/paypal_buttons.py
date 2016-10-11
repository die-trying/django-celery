from django import template
from django.template import Context
from django.template.loader import get_template

register = template.Library()


@register.simple_tag
def buy_now(button_id):
    tpl = get_template('products/_paypal/buy_now.html')
    return tpl.render(Context({
        'button_id': button_id,
    }))
