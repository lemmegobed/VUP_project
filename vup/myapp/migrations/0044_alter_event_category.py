# Generated by Django 5.1.5 on 2025-03-02 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0043_delete_advertisement_alter_event_category_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="category",
            field=models.CharField(max_length=15),
        ),
    ]
