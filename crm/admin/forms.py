from django import forms
from suit.widgets import SuitDateWidget

from elk.admin.forms import ActionFormWithParams


class CustomerActionForm(ActionFormWithParams):
    start = forms.DateField(widget=SuitDateWidget(attrs={'class': 'customer-action__date-selector'}))
    end = forms.DateField(widget=SuitDateWidget(attrs={'class': 'customer-action__date-selector'}))
