# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-18 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0016_auto_20181211_2116'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=4000, verbose_name='Tip')),
                ('created', models.DateTimeField(editable=False)),
            ],
        ),
    ]