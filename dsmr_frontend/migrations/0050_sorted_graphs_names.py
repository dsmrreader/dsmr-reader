# Generated by Django 3.2.22 on 2023-10-23 17:37

from django.db import migrations


def migrate_forward(apps, schema_editor):
    GRAPH_TYPE_ELECTRICITY = "electricity"
    GRAPH_TYPE_PHASES = "phases"
    GRAPH_TYPE_VOLTAGE = "voltage"
    GRAPH_TYPE_POWER_CURRENT = "power_current"
    GRAPH_TYPE_GAS = "gas"
    GRAPH_TYPE_WEATHER = "weather"
    GRAPH_TYPE_ELECTRICITY_PEAKS = "electricity-peaks"

    SortedGraph = apps.get_model("dsmr_frontend", "SortedGraph")
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_ELECTRICITY).update(
        name="Recent Electricity usage"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_PHASES).update(
        name="Recent phase usage"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_VOLTAGE).update(
        name="Recent phase voltages"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_POWER_CURRENT).update(
        name="Recent phase currents"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_GAS).update(
        name="Recent gas consumption"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_WEATHER).update(
        name="Recent temperatures"
    )
    SortedGraph.objects.filter(graph_type=GRAPH_TYPE_ELECTRICITY_PEAKS).update(
        name="Recent quarter hour electricity peak consumption"
    )


def migrate_backward(apps, schema_editor):
    # No-op. Idempotent when running migrate_forward() again.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_frontend", "0049_alter_notification_options"),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
    ]