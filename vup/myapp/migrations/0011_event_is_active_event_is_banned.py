# Generated by Django 5.1.3 on 2025-01-24 08:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0010_alter_event_province_alter_report_report_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="event",
            name="is_banned",
            field=models.BooleanField(default=False),
        ),
    ]
