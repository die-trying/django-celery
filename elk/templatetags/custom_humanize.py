from django import template
from django.contrib.humanize.templatetags import humanize
from django.utils.translation import pgettext

register = template.Library()


@register.filter
def naturaltime(value):
    """
    Custom wrapper over django.contrib.humanize.naturaltime
    """
    time = humanize.naturaltime(value)
    time = time.replace(' ' + pgettext('naturaltime', 'from now'), '')
    return time
