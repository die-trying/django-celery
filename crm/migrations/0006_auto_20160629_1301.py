# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20160628_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='source',
            field=models.ForeignKey(to='crm.CustomerSource', on_delete=django.db.models.deletion.PROTECT, default=1),
        ),
    ]
