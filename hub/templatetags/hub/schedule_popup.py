from django import template

register = template.Library()


@register.simple_tag
def lesson_type_filter(types):
    """
    Generate buttons for lesson planning filter. Outputs a button only if lesson
    can be planned directly.
    """

    button = """<label class = "btn btn-primary {classes}"><input type="radio" name="lesson_type" {checked} value = "{val}">{name}</label>"""
    first = True
    result = ''
    for lesson_type in types:
        if not lesson_type.model_class().can_be_directly_planned():
            continue

        classes = ''
        checked = ''
        if first:  # for bootstrap the first button should be checked manualy
            first = False
            classes = 'active'
            checked = 'checked'

        result += button.format(
            classes=classes,
            checked=checked,
            val=lesson_type.pk,
            name=lesson_type.model_class()._meta.verbose_name_plural
        )
    return result
