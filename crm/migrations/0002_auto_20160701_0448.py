# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def add_internal_customer_src(app, schema_editor):
    CustomerSource = app.get_model('crm', 'CustomerSource')

    internal_src = CustomerSource(
        name='internal'
    )
    internal_src.save()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSource',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
            ],
        ),
        migrations.RemoveField(
            model_name='customer',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='last_name',
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_first_name',
            field=models.CharField(blank=True, max_length=140, verbose_name='First name'),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_last_name',
            field=models.CharField(blank=True, max_length=140, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, null=True, to=settings.AUTH_USER_MODEL, blank=True, related_name='crm'),
        ),
        migrations.RunPython(add_internal_customer_src),
        migrations.AddField(
            model_name='customer',
            name='source',
            field=models.ForeignKey(to='crm.CustomerSource', on_delete=django.db.models.deletion.PROTECT, default=1),
        ),
    ]
