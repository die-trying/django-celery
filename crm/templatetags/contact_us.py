from django import template

register = template.Library()


@register.simple_tag
def contact_us(text='Contact us', classes=''):
    return '<a href="#" class="%s" data-toggle="modal" data-target="#issue-popup">%s</a>' % (classes, text)
