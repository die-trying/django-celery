# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_tiers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tier',
            name='name',
            field=models.CharField(max_length=140, verbose_name='Tier name'),
        ),
    ]
