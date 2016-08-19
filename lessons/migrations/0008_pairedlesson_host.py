# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0009_auto_20160813_1302'),
        ('lessons', '0007_auto_20160728_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='pairedlesson',
            name='host',
            field=models.ForeignKey(related_name='+', null=True, to='teachers.Teacher'),
        ),
    ]
