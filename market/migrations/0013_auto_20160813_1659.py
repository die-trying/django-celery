# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_auto_20160810_1245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'verbose_name': 'Lesson', 'get_latest_by': 'buy_date'},
        ),
    ]
