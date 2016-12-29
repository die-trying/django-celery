# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0011_unique_lesson_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'permissions': (('other_entries', "Can work with other's timeleine entries"),), 'verbose_name': 'Planned class', 'verbose_name_plural': 'Planned classes', 'ordering': ['start']},
        ),
    ]
