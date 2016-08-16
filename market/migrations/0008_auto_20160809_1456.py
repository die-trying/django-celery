# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_auto_20160805_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='buy_source',
            field=models.CharField(default='single', max_length=12),
        ),
    ]
