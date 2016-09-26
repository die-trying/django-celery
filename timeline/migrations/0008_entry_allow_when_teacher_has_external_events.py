# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0007_entry_allow_when_teacher_is_busy'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='allow_when_teacher_has_external_events',
            field=models.BooleanField(default=True),
        ),
    ]
