# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0009_auto_20160809_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='is_fully_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_fully_used',
            field=models.BooleanField(default=False),
        ),
    ]
