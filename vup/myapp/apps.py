from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    # def ready(self):
    #     """เรียก Scheduler เมื่อแอป Django เริ่มทำงาน"""
    #     from myapp.scheduler import start
    #     start()