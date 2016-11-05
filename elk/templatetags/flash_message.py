from django import template

register = template.Library()


@register.simple_tag
def flash_message(msg, level='info'):
    """
    Display an autoclosing flash message
    """
    return """
    <div class="flash-message alert alert-{level} alert-dismissible fade in fadein" role="alert">
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
             <span aria-hidden="true">&times;</span>
        </button>
        {msg}
    </div>
    """.format(
        level=level.lower(),
        msg=msg,
    )
