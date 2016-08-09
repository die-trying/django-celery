# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0005_auto_20160801_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
    ]
