# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_auto_20160719_0735'),
        ('teachers', '0005_teacher_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lessonwithnative',
            options={'verbose_name_plural': 'Native speakers', 'verbose_name': 'Native speaker session'},
        ),
        migrations.AlterModelOptions(
            name='ordinarylesson',
            options={'verbose_name': 'Curated session'},
        ),
    ]
