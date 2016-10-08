from django import template

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
    return '<a class="skype skype-%s" href="skype:%s?%s">%s</a>' % (action, skype_username, action, skype_username)
