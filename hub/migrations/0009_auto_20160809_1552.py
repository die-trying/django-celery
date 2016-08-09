# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0008_auto_20160809_1456'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='buy_time',
            new_name='buy_date',
        ),
        migrations.RemoveField(
            model_name='class',
            name='buy_time',
        ),
    ]
