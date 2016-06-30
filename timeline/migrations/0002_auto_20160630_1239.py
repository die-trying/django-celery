# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'Entries'},
        ),
        migrations.AlterField(
            model_name='entry',
            name='customer',
            field=models.ForeignKey(null=True, to='crm.Customer', blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planned_lessons'),
        ),
    ]
