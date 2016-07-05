# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_auto_20160701_0448'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='facebook',
            field=models.CharField(verbose_name='Facebook profile id', max_length=140, blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='instagram',
            field=models.CharField(verbose_name='Instagram username', max_length=140, blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='skype',
            field=models.CharField(verbose_name='Skype login', max_length=140, blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='twitter',
            field=models.CharField(verbose_name='Twitter username', max_length=140, blank=True),
        ),
    ]
