from django import template

register = template.Library()


@register.simple_tag
def lesson_type_filter_btn(lesson_type):
    """
    A button for lesson planning filter. Outputs a button only if lesson can be
    planned directly.
    """
    if not lesson_type.model_class().can_be_directly_planned():
        return ''
    return """<label class = "btn btn-primary">
                <input type="radio" name="lesson_type" value = "%d">%s</label>""" \
                % (lesson_type.pk, lesson_type.model_class()._meta.verbose_name_plural)
