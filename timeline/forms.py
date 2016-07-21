from django import forms

from timeline.models import Entry as TimelineEntry


class EntryForm(forms.ModelForm):
    class Meta:
        fields = ('lesson_type', 'lesson_id', 'teacher', 'start')
        localized_fields = ('start',)
        model = TimelineEntry
        widgets = {
            'start': forms.SplitDateTimeWidget(),
            'lesson_id': forms.Select(),                # populated by calendar.coffee
            'teacher': forms.HiddenInput()              # populated in the template
        }
