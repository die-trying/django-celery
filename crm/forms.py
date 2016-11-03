from django import forms

from crm.models import Customer


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('timezone', 'birthday', 'skype')
        localized_fields = ('birthday',)
        widgets = {
            'timezone': forms.Select(attrs={'class': 'form-control selectpicker customer-profile__timezone', 'data-live-search': 'true'}),
        }
