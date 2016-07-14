from django import forms

from timeline.models import Entry as TimelineEntry


class EntryForm(forms.ModelForm):
    class Meta:
        fields = ('lesson_type', 'lesson_id', 'teacher', 'start_time', 'duration')
        model = TimelineEntry
        widgets = {
            'start_time': forms.SplitDateTimeWidget(),
            'lesson_id': forms.Select(),                # populated by js/calendar.coffee
            'teacher': forms.HiddenInput()              # populated in the template
        }
