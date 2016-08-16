# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('src', models.CharField(verbose_name='Event source', choices=[('customer', 'customer'), ('teacher', 'Teacher')], max_length=10, default='customer')),
                ('ip', models.GenericIPAddressField(default='127.0.0.1')),
                ('raw_useragent', models.TextField()),
                ('is_mobile', models.NullBooleanField()),
                ('is_tablet', models.NullBooleanField()),
                ('is_pc', models.NullBooleanField(max_length=140)),
                ('browser_family', models.CharField(max_length=140, null=True)),
                ('browser_version', models.CharField(max_length=140, null=True)),
                ('os_family', models.CharField(max_length=140, null=True)),
                ('os_version_string', models.CharField(max_length=140, null=True)),
                ('device', models.CharField(max_length=140, null=True)),
                ('event_type', models.CharField(max_length=5, verbose_name='Event type', choices=[('SCHED', 'Scheduling'), ('CANCEL', 'Cancellation'), ('RESCH', 'Rescheduling')], db_index=True)),
                ('scheduled_class', models.ForeignKey(to='market.Class')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='paymentevent',
            name='src',
            field=models.CharField(verbose_name='Event source', choices=[('customer', 'customer'), ('teacher', 'Teacher')], max_length=10, default='customer'),
        ),
    ]
