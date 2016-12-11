from django import forms
from django.contrib.admin.helpers import ActionForm
from suit.widgets import SuitDateWidget


class CustomerActionForm(ActionForm):
    start = forms.DateField(widget=SuitDateWidget(attrs={'class': 'customer-action__date-selector'}))
    end = forms.DateField(widget=SuitDateWidget(attrs={'class': 'customer-action__date-selector'}))
