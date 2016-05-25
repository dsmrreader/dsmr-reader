# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import colorfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0003_drop_history_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontendsettings',
            name='electricity_delivered_alternate_color',
            field=colorfield.fields.ColorField(help_text='Graph color for electricity delivered (low tariff)', default='#7D311A', verbose_name='Electricity delivered color (alternative)', max_length=10),
        ),
        migrations.AddField(
            model_name='frontendsettings',
            name='electricity_delivered_color',
            field=colorfield.fields.ColorField(help_text='Graph color for electricity delivered (default + high tariff)', default='#F05050', verbose_name='Electricity delivered color', max_length=10),
        ),
        migrations.AddField(
            model_name='frontendsettings',
            name='electricity_returned_alternate_color',
            field=colorfield.fields.ColorField(help_text='Graph color for electricity returned (low tariff)', default='#C8C864', verbose_name='Electricity returned color (alternative)', max_length=10),
        ),
        migrations.AddField(
            model_name='frontendsettings',
            name='electricity_returned_color',
            field=colorfield.fields.ColorField(help_text='Graph color for electricity returned (default + high tariff)', default='#27C24C', verbose_name='Electricity returned color', max_length=10),
        ),
        migrations.AddField(
            model_name='frontendsettings',
            name='gas_delivered_color',
            field=colorfield.fields.ColorField(help_text='Graph color for gas delivered', default='#FF851B', verbose_name='Gas delivered color', max_length=10),
        ),
        migrations.AddField(
            model_name='frontendsettings',
            name='temperature_color',
            field=colorfield.fields.ColorField(help_text='Graph color for temperatures read', default='#0073B7', verbose_name='Temperature color', max_length=10),
        ),
    ]
