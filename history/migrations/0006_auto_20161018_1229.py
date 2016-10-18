# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('history', '0005_auto_20161016_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentevent',
            name='payment',
        ),
        migrations.AddField(
            model_name='paymentevent',
            name='payment_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentevent',
            name='payment_type',
            field=models.ForeignKey(default=1, to='contenttypes.ContentType', on_delete=django.db.models.deletion.PROTECT, related_name='+'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paymentevent',
            name='product_type',
            field=models.ForeignKey(related_name='+', to='contenttypes.ContentType'),
        ),
    ]
