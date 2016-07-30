from django import template

register = template.Library()


@register.filter
def format_entry_date(fields):
    date = fields.field.widget.widgets[0]
    time = fields.field.widget.widgets[1]

    date.attrs['required'] = 'true'
    time.attrs['required'] = 'true'

    time.attrs['placeholder'] = '12:30'

    date.attrs['placeholder'] = 'mm/dd/yy'
    date.format = '%m/%d/%Y'  # flex scope

    time.format = '%H:%M'

    date.attrs['class'] = 'form-control'
    time.attrs['class'] = 'form-control'

    # date.attrs['rv-value'] = 'model.start_date'
    # time.attrs['rv-value'] = 'model.start_time'

    return fields
