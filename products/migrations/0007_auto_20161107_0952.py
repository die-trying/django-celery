# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def rename_single_lesson_product(apps, schema_editor):
    SingleLessonProduct = apps.get_model('products.SingleLessonProduct')
    SingleLessonProduct.objects.update(
        name='Single lesson',
        internal_name='Single lesson product'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_tier_paypal_button_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='singlelessonproduct',
            options={'verbose_name': 'Single lesson'},
        ),
        migrations.RunPython(rename_single_lesson_product),
    ]
