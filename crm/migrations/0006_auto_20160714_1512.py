# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_auto_20160707_0716'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisteredCustomer',
            fields=[
            ],
            options={
                'verbose_name': 'Student',
                'proxy': True,
            },
            bases=('crm.customer',),
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Lead'},
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile_photo',
            field=models.ImageField(null=True, upload_to='profiles/', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='source',
            field=models.CharField(default='internal', max_length=140),
        ),
    ]
