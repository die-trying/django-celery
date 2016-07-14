# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='customer',
            field=models.ForeignKey(related_name='classes', to='crm.Customer'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='customer',
            field=models.ForeignKey(related_name='subscriptions', to='crm.Customer'),
        ),
    ]
