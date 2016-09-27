# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import image_cropping.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0018_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='profile_photo_cropping',
            field=image_cropping.fields.ImageRatioField('image', '80x80', verbose_name='profile photo cropping', free_crop=False, size_warning=False, hide_image_field=False, allow_fullsize=False, adapt_rotation=False, help_text=None),
        ),
    ]
