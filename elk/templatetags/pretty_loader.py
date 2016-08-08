from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def pretty_loader():
    return 'style="background-image: url(\'%s\')"' % static('i/loader.svg')
