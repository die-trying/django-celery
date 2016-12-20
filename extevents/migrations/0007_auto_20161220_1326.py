# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extevents', '0006_auto_20160924_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalevent',
            name='description',
            field=models.TextField(),
        ),
    ]
