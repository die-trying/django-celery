# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0011_auto_20160809_1853'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'verbose_name': 'Bought lesson', 'get_latest_by': 'buy_date'},
        ),
    ]
