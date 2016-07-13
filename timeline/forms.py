from django import forms

from timeline.models import Entry as TimelineEntry


class EntryForm(forms.ModelForm):
    class Meta:
        fields = ('event_type', 'event_id', 'teacher', 'start_time', 'duration')
        model = TimelineEntry
        widgets = {
            'event_id': forms.Select(),  # populated by js/calendar.coffee
            'teacher': forms.HiddenInput()  # populated in the template
        }
