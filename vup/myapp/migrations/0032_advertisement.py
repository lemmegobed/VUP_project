# Generated by Django 5.1.5 on 2025-01-29 16:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0031_alter_chat_message_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Advertisement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="ads/")),
                ("link", models.URLField()),
                ("keyword", models.CharField(max_length=255)),
            ],
        ),
    ]
