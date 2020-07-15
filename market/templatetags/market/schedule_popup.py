from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag
def lesson_type_filter(types):
    """
    Generate buttons for lesson planning filter. Outputs a button only if lesson
    can be planned directly.
    """

    button = """<label class = "btn btn-default {classes}"><input type="radio" name="lesson_type" {checked} data-query-type="{query_type}" value = "{val}">{name}</label>"""
    first = True
    result = ''
    for lesson_type in types:
        if not lesson_type.model_class().can_be_directly_planned():
            continue

        query_type = 'teachers'
        if lesson_type.model_class().timeline_entry_required():
            query_type = 'lessons'

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
            query_type=query_type,  # what popup should query — available teachers (for regular lessons), or avaialbe slots (for lesson_types)
            name=lesson_type.model_class()._meta.verbose_name
        )
    return mark_safe(result)


@register.simple_tag
def schedule_popup_title(lesson_types):
    """
    Title for scheduling popup

    When user has only one lesson type, the popup is titled 'Schedule a <lesson_type>'
    i.e. 'Schedule a master class' or 'Schedule a curated session'

    When there are multiple lesson types with filter — 'Schedule a lesson'.
    """
    if len(lesson_types) > 1:
        return _('lesson')
    else:
        if lesson_types:
            return lesson_types[0].model_class()._meta.verbose_name.lower()
