# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-09-12 03:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='studio',
            new_name='shooting',
        ),
    ]