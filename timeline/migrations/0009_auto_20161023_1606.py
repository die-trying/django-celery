# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0008_entry_allow_when_teacher_has_external_events'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='allow_overlap',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='allow_when_teacher_has_external_events',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='allow_when_teacher_is_busy',
        ),
    ]
