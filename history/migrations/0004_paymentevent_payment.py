# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('history', '0003_auto_20161014_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentevent',
            name='payment',
            field=models.ForeignKey(default=0, related_name='history_record', to='payments.Payment'),
            preserve_default=False,
        ),
    ]
