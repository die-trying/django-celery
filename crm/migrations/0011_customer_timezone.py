# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import timezone_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_customer_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='Europe/Moscow'),
        ),
    ]
