# Generated by Django 5.1.5 on 2025-01-31 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0036_notification_is_sent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="is_sent",
            field=models.BooleanField(default=True),
        ),
    ]
