# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-10-23 04:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("dashboard", "0010_remove_consumption_pmtct_consumption")]

    operations = [
        migrations.RenameField(
            model_name="consumption",
            old_name="art_consumption",
            new_name="combined_consumption",
        )
    ]
