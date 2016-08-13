# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0008_auto_20160811_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='current_level',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[('A1', 'A1'), ('B1', 'B1'), ('C1', 'C1'), ('A2', 'A2'), ('B2', 'B2'), ('C2', 'C2'), ('A3', 'A3'), ('B3', 'B3'), ('C3', 'C3')]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='starting_level',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[('A1', 'A1'), ('B1', 'B1'), ('C1', 'C1'), ('A2', 'A2'), ('B2', 'B2'), ('C2', 'C2'), ('A3', 'A3'), ('B3', 'B3'), ('C3', 'C3')]),
        ),
    ]
