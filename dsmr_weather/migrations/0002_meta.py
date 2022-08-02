# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_weather", "0001_weather_models"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="temperaturereading",
            options={"default_permissions": ()},
        ),
        migrations.AlterModelOptions(
            name="weathersettings",
            options={
                "verbose_name": "Weather configuration",
                "default_permissions": (),
            },
        ),
        migrations.AlterField(
            model_name="temperaturereading",
            name="degrees_celcius",
            field=models.DecimalField(
                decimal_places=1, verbose_name="Temperature (in ℃)", max_digits=4
            ),
        ),
        migrations.AlterField(
            model_name="weathersettings",
            name="buienradar_station",
            field=models.IntegerField(
                choices=[
                    (6391, "Weather station Arcen"),
                    (6275, "Weather station Arnhem"),
                    (6249, "Weather station Berkhout"),
                    (6308, "Weather station Cadzand"),
                    (6260, "Weather station De Bilt"),
                    (6235, "Weather station Den Helder"),
                    (6370, "Weather station Eindhoven"),
                    (6377, "Weather station Ell"),
                    (6321, "Weather station Euro platform"),
                    (6350, "Weather station Gilze Rijen"),
                    (6283, "Weather station Groenlo-Hupsel"),
                    (6280, "Weather station Groningen"),
                    (6315, "Weather station Hansweert"),
                    (6278, "Weather station Heino"),
                    (6356, "Weather station Herwijnen"),
                    (6330, "Weather station Hoek van Holland"),
                    (6311, "Weather station Hoofdplaat"),
                    (6279, "Weather station Hoogeveen"),
                    (6251, "Weather station Hoorn Terschelling"),
                    (6258, "Weather station Houtribdijk"),
                    (6285, "Weather station Huibertgat"),
                    (6209, "Weather station IJmond"),
                    (6225, "Weather station IJmuiden"),
                    (6210, "Weather station Katwijk"),
                    (6277, "Weather station Lauwersoog"),
                    (6320, "Weather station LE Goeree"),
                    (6270, "Weather station Leeuwarden"),
                    (6269, "Weather station Lelystad"),
                    (6348, "Weather station Lopik-Cabauw"),
                    (6380, "Weather station Maastricht"),
                    (6273, "Weather station Marknesse"),
                    (6286, "Weather station Nieuw Beerta"),
                    (6312, "Weather station Oosterschelde"),
                    (6344, "Weather station Rotterdam"),
                    (6343, "Weather station Rotterdam Geulhaven"),
                    (6316, "Weather station Schaar"),
                    (6240, "Weather station Schiphol"),
                    (6324, "Weather station Stavenisse"),
                    (6267, "Weather station Stavoren"),
                    (6331, "Weather station Tholen"),
                    (6290, "Weather station Twente"),
                    (6313, "Weather station Vlakte aan de Raan"),
                    (6242, "Weather station Vlieland"),
                    (6310, "Weather station Vlissingen"),
                    (6375, "Weather station Volkel"),
                    (6215, "Weather station Voorschoten"),
                    (6319, "Weather station Westdorpe"),
                    (6248, "Weather station Wijdenes"),
                    (6257, "Weather station Wijk aan Zee"),
                    (6340, "Weather station Woensdrecht"),
                    (6239, "Weather station Zeeplatform F-3"),
                    (6252, "Weather station Zeeplatform K13"),
                ],
                verbose_name="Buienradar weather station",
                help_text="The weather station used to measure and log outside temperatures. Choose one nearby.",
                default=6260,
            ),
        ),
    ]
