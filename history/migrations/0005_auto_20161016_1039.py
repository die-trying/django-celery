# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0004_paymentevent_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classevent',
            name='raw_useragent',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='paymentevent',
            name='raw_useragent',
            field=models.TextField(null=True),
        ),
    ]
