# Generated by Django 5.1.5 on 2025-02-02 16:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0040_alter_event_has_ended"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="is_scheduled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notification",
            name="scheduled_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
