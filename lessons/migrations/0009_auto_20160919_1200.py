# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0008_pairedlesson_host'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lessonwithnative',
            options={'verbose_name_plural': 'Native speaker sessions', 'verbose_name': 'Native speaker'},
        ),
        migrations.AlterModelOptions(
            name='ordinarylesson',
            options={'verbose_name_plural': 'Single lessons', 'verbose_name': 'Single session'},
        ),
        migrations.AlterModelOptions(
            name='pairedlesson',
            options={'verbose_name_plural': 'Paired lessons', 'verbose_name': 'Paired session'},
        ),
    ]
