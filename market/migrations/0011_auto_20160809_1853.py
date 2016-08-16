# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0010_auto_20160809_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='product_id',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
