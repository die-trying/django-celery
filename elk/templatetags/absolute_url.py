from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.template.defaulttags import URLNode, url

register = template.Library()


class AbsoluteURLNode(URLNode):
    """
    Thanks to http://felecan.com/2013/django-templatetag-absolute-full-url-domain-path/
    """
    def render(self, context):
        path = super().render(context)

        if self.asvar:
            context[self.asvar] = urljoin(settings.ABSOLUTE_HOST, context[self.asvar])
            return ''
        else:
            return urljoin(settings.ABSOLUTE_HOST, path)


@register.tag
def absolute_url(parser, token, node_cls=AbsoluteURLNode):
    """
    Just like {% url %} but adds the domain from settings.ABSOLUTE_HOST.
    """
    node_instance = url(parser, token)

    return node_cls(
        view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar
    )
