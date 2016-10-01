# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0019_customer_profile_photo_cropping'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, verbose_name='Phone number', max_length=15),
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile_photo_cropping',
            field=image_cropping.fields.ImageRatioField('profile_photo', '80x80', hide_image_field=False, free_crop=False, adapt_rotation=False, verbose_name='profile photo cropping', help_text=None, allow_fullsize=False, size_warning=False),
        ),
    ]
