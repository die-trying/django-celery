# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_auto_20160929_0355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='active',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='class',
            name='is_fully_used',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='active',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='is_fully_used',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
