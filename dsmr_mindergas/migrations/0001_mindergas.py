# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MinderGasSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                (
                    "export",
                    models.BooleanField(
                        default=False,
                        verbose_name="Export data to MinderGas",
                        help_text="Whether we should export your gas readings (if any) to your MinderGas.nl account. DSMR-reader transmits the last reading of the previous day to your account.",
                    ),
                ),
                (
                    "auth_token",
                    models.CharField(
                        blank=True,
                        null=True,
                        default=None,
                        help_text="The authentication token used to authenticate for the MinderGas API. More information can be found here: https://www.mindergas.nl/member/api",
                        max_length=64,
                        verbose_name="MinderGas authentication token",
                    ),
                ),
                (
                    "next_export",
                    models.DateField(
                        blank=True,
                        null=True,
                        default=None,
                        verbose_name="Next export",
                        help_text="Timestamp of the next export. Automatically updated by application.",
                    ),
                ),
            ],
            options={
                "default_permissions": (),
                "verbose_name": "MinderGas.nl configuration",
            },
        ),
    ]
