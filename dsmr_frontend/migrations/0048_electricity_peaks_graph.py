# Generated by Django 3.2.14 on 2022-07-25 20:06


from django.db import migrations, models


def migrate_forward(apps, schema_editor):
    SortedGraph = apps.get_model("dsmr_frontend", "SortedGraph")
    SortedGraph.objects.create(
        name="Electricity quarter hour peaks",
        graph_type="electricity-peaks",
        sorting_order=7,
    )


def migrate_backward(apps, schema_editor):
    SortedGraph = apps.get_model("dsmr_frontend", "SortedGraph")
    SortedGraph.objects.get(graph_type="electricity-peaks").delete()


class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
    ]

    dependencies = [
        ("dsmr_frontend", "0047_tariff_name_update"),
    ]
