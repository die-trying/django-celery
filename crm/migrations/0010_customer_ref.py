# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_auto_20160813_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='ref',
            field=models.CharField(verbose_name='Referal code', max_length=140, blank=True),
        ),
    ]
