from django import forms

from crm.models import Customer
from elk.utils.date import common_timezones


class CustomerProfileForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        choices=common_timezones(),
        widget=forms.Select(
            attrs={
                'class': 'form-control selectpicker customer-profile__timezone fadein',
                'data-live-search': 'true'
            }
        ),
    )

    class Meta:
        model = Customer
        fields = ('timezone', 'birthday', 'skype')
        localized_fields = ('birthday',)
