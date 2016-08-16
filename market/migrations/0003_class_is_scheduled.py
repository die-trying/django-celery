# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_auto_20160714_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='is_scheduled',
            field=models.BooleanField(default=False),
        ),
    ]
