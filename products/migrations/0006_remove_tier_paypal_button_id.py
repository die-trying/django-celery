# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_singlelessonproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tier',
            name='paypal_button_id',
        ),
    ]
