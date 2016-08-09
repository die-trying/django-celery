# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0007_auto_20160802_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workinghours',
            name='end',
            field=models.TimeField(verbose_name='End hoour(EDT)'),
        ),
        migrations.AlterField(
            model_name='workinghours',
            name='start',
            field=models.TimeField(verbose_name='Start hour (EDT)'),
        ),
    ]
