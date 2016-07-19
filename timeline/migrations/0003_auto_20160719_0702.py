# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


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
