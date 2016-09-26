# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extevents', '0003_googlecalendar_last_update'),
    ]

    operations = [
        migrations.RenameField(
            model_name='externalevent',
            old_name='ext_src_id',
            new_name='src_id',
        ),
        migrations.RenameField(
            model_name='externalevent',
            old_name='ext_src_type',
            new_name='src_type',
        ),
        migrations.AlterUniqueTogether(
            name='externalevent',
            unique_together=set([('teacher', 'src_type', 'src_id', 'start', 'end')]),
        ),
    ]
