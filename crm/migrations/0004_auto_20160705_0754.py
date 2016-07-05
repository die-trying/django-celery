# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_auto_20160705_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='profile_photo',
            field=models.ImageField(null=True, upload_to='profiles/'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='source',
            field=models.CharField(max_length=140, verbose_name='Customer source', default='internal'),
        ),
    ]
