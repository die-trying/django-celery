# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0006_entry_is_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='allow_when_teacher_is_busy',
            field=models.BooleanField(default=True),
        ),
    ]
