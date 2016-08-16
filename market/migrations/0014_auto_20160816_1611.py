# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0013_auto_20160813_1659'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'get_latest_by': 'buy_date', 'verbose_name': 'Purchsed lesson'},
        ),
    ]
