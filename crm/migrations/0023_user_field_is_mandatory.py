# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


def drop_customer_profiles_without_user(apps, schema_editor):
    Customer = apps.get_model('crm.Customer')
    Customer.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0022_auto_20161220_1234'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE'),
        migrations.RunPython(drop_customer_profiles_without_user),
        migrations.AlterField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='crm'),
        ),
    ]
