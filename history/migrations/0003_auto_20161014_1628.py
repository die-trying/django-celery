# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_auto_20160807_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentevent',
            name='customer',
            field=models.ForeignKey(to='crm.Customer', related_name='payment_events'),
        ),
    ]
