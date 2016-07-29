# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0002_entry_allow_overlap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timeline_entries', to='teachers.Teacher'),
        ),
    ]
