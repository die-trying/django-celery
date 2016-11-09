from django.forms.widgets import Select


class ForeignKeyWidget(Select):
    """
    Fancy select widget based on Select2 (https://select2.github.io/)
    """
    def __init__(self, attrs={}, **kwargs):

        classes = attrs.get('class', '')
        classes = 'foreign_key ' + classes

        attrs['class'] = classes

        super().__init__(attrs, **kwargs)
