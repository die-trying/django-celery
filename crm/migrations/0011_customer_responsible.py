# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0010_teacher_active'),
        ('crm', '0010_customer_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='responsible',
            field=models.ForeignKey(related_name='patronized_customers', to='teachers.Teacher', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
    ]
