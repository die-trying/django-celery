from django import forms
from django.contrib.admin.helpers import ActionForm
from django.utils.translation import ugettext_lazy as _


class ActionFormWithParams(ActionForm):
    """
    Use this form when you are redefining an ActionForm
    in order to add some action parameters.
    """
    action = forms.ChoiceField(label=_('Action:'), widget=forms.widgets.Select(attrs={'class': 'action_selector'}))
