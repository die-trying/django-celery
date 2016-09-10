# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_customer_responsible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=140)),
                ('legal_name', models.CharField(max_length=140)),
            ],
            options={
                'verbose_name_plural': 'companies',
            },
        ),
        migrations.DeleteModel(
            name='RegisteredCustomer',
        ),
        migrations.AddField(
            model_name='customer',
            name='company',
            field=models.ForeignKey(to='crm.Company', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', blank=True),
        ),
    ]
