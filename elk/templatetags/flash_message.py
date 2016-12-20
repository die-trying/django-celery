from django import template

register = template.Library()

DJANGO_BOOTSTRAP_ALERT_LEVEL_MAPPING = {
    'error': 'danger',
    #'django': 'bootstrap'
}


def map_django_alert_level_to_bootstrap(tags):
    result_tags = []
    for tag in tags.split(' '):
        if tag in DJANGO_BOOTSTRAP_ALERT_LEVEL_MAPPING:
            tag = DJANGO_BOOTSTRAP_ALERT_LEVEL_MAPPING[tag]

        result_tags.append('alert-' + tag)

    return ' '.join(result_tags)


@register.simple_tag
def flash_message(msg, tags='info'):
    """
    Display an autoclosing flash message
    """
    tags = map_django_alert_level_to_bootstrap(tags)
    return """
    <div class="flash-message alert {tags} alert-dismissible fade in fadein" role="alert">
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
             <span aria-hidden="true">&times;</span>
        </button>
        {msg}
    </div>
    """.format(
        tags=tags,
        msg=msg,
    )
