# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20160705_0754'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='linkedin',
            field=models.CharField(blank=True, max_length=140, verbose_name='Linkedin username'),
        ),
        migrations.AddField(
            model_name='customer',
            name='native_language',
            field=models.CharField(blank=True, max_length=140, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='profession',
            field=models.CharField(blank=True, max_length=140, null=True),
        ),
    ]
