# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manual_class_logging', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manualclasslogentry',
            options={'verbose_name': 'Completed class', 'verbose_name_plural': 'Completed classes'},
        ),
        migrations.AlterField(
            model_name='manualclasslogentry',
            name='Class',
            field=models.ForeignKey(to='market.Class', related_name='manualy_completed_classes'),
        ),
        migrations.AlterField(
            model_name='manualclasslogentry',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
