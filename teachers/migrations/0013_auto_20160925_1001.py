# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0012_auto_20160910_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workinghours',
            name='end',
            field=models.TimeField(verbose_name='End hour (EDT)'),
        ),
        migrations.AlterField(
            model_name='workinghours',
            name='start',
            field=models.TimeField(verbose_name='Start hour (EDT)'),
        ),
    ]
