# Generated by Django 5.1.3 on 2025-01-23 15:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0004_alter_report_report_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="is_banned",
            field=models.BooleanField(default=False),
        ),
    ]
