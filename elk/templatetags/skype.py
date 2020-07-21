from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def skype_chat(crm):
    if not crm or not len(crm.skype):
        return ''

    return _skype_link(crm.skype, 'chat')


@register.simple_tag
def skype_call(crm):
    if not crm or not len(crm.skype):
        return ''

    return _skype_link(crm.skype, 'call')


def _skype_link(skype_username, action='chat'):
    return format_html('<a class="skype skype-{}" href="skype:{}?{}">{}</a>', action, skype_username, action, skype_username)
