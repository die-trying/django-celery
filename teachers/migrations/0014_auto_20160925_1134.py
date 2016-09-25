# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0013_auto_20160925_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='announce',
            field=models.TextField(max_length=140),
        ),
    ]
