# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-01-25 04:16
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [("dashboard", "0034_test_definitions")]

    operations = [
        migrations.RemoveField(model_name="score", name="MULTIPLE_ORDERS"),
        migrations.RemoveField(model_name="score", name="OrderFormFreeOfGaps"),
        migrations.RemoveField(model_name="score", name="REPORTING"),
        migrations.RemoveField(model_name="score", name="WEB_BASED"),
        migrations.RemoveField(
            model_name="score", name="closingBalanceMatchesOpeningBalance"
        ),
        migrations.RemoveField(model_name="score", name="consumptionAndPatients"),
        migrations.RemoveField(model_name="score", name="differentOrdersOverTime"),
        migrations.RemoveField(model_name="score", name="guidelineAdherenceAdult1L"),
        migrations.RemoveField(model_name="score", name="guidelineAdherenceAdult2L"),
        migrations.RemoveField(model_name="score", name="guidelineAdherencePaed1L"),
        migrations.RemoveField(model_name="score", name="nnrtiAdults"),
        migrations.RemoveField(model_name="score", name="nnrtiPaed"),
        migrations.RemoveField(
            model_name="score", name="orderFormFreeOfNegativeNumbers"
        ),
        migrations.RemoveField(model_name="score", name="stableConsumption"),
        migrations.RemoveField(model_name="score", name="stablePatientVolumes"),
        migrations.RemoveField(model_name="score", name="warehouseFulfilment"),
        migrations.AddField(
            model_name="score",
            name="data",
            field=jsonfield.fields.JSONField(default="{}"),
            preserve_default=False,
        ),
    ]
