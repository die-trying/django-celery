from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def contact_us(text='Contact us', classes=''):
    return format_html('<a href="#" class="{}" data-toggle="modal" data-target="#issue-popup">{}</a>', classes, text)
