# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0004_auto_20160713_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='happyhour',
            name='host',
            field=models.ForeignKey(to='teachers.Teacher', related_name='+', null=True),
        ),
        migrations.AlterField(
            model_name='masterclass',
            name='host',
            field=models.ForeignKey(to='teachers.Teacher', related_name='+', null=True),
        ),
    ]
