# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-04-01 05:45
from __future__ import unicode_literals

from django.db import migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0045_test_definitions_with_tracers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracingformulations',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from=[u'name']),
        ),
    ]