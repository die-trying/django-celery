# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0004_entry_allow_besides_working_hours'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name': 'Planned class', 'verbose_name_plural': 'Planned classes', 'permissions': (('other_entries', "Can work with other's timeleine entries"),)},
        ),
        migrations.RemoveField(
            model_name='entry',
            name='customers',
        ),
        migrations.AlterField(
            model_name='entry',
            name='slots',
            field=models.SmallIntegerField(verbose_name='Student slots', default=1),
        ),
        migrations.AlterField(
            model_name='entry',
            name='taken_slots',
            field=models.SmallIntegerField(verbose_name='Students', default=0),
        ),
    ]
