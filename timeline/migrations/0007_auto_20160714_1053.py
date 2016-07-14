# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0006_auto_20160713_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='lesson_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
    ]
