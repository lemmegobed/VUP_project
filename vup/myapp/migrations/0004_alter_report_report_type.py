# Generated by Django 5.1.3 on 2025-01-22 17:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_alter_report_options_alter_report_event_owner_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="report_type",
            field=models.CharField(
                choices=[
                    ("ความผิดพลาดของระบบ", "ความผิดพลาดของระบบ"),
                    ("พฤติกรรมไม่เหมาะสม", "พฤติกรรมไม่เหมาะสม"),
                    ("Other", "อื่นๆ"),
                ],
                max_length=50,
                null=True,
                verbose_name="ประเภทการรายงาน",
            ),
        ),
    ]
