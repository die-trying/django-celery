# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0010_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordinarylesson',
            options={'verbose_name': 'Single lesson', 'verbose_name_plural': 'Single lessons'},
        ),
        migrations.AlterModelOptions(
            name='pairedlesson',
            options={'verbose_name': 'Paired lesson', 'verbose_name_plural': 'Paired lessons'},
        ),
    ]
