# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordinarylesson',
            options={'verbose_name': 'Usual curated lesson'},
        ),
        migrations.AlterModelOptions(
            name='product1',
            options={'verbose_name': 'Subscription type: first subscription', 'verbose_name_plural': 'Subscriptions of the first type'},
        ),
        migrations.AddField(
            model_name='lessonwithnative',
            name='active',
            field=models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')]),
        ),
        migrations.AddField(
            model_name='ordinarylesson',
            name='active',
            field=models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')]),
        ),
    ]
