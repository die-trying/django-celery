# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0004_entry_duration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='event_id',
            new_name='lesson_id',
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='event_type',
            new_name='lesson_type',
        ),
    ]
