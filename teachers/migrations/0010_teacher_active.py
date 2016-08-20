# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0009_auto_20160813_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='active',
            field=models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')]),
        ),
    ]
