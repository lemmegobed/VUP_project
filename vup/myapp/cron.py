# import logging
# from django_cron import CronJobBase, Schedule
# from django.utils.timezone import now
# from myapp.models import Notification

# logger = logging.getLogger(__name__)

# class UpdateScheduledNotifications(CronJobBase):
#     """อัปเดตแจ้งเตือนที่ถึงเวลาให้แสดง"""
#     RUN_EVERY_MINS = 1  # ✅ ให้รันทุก 1 นาที
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = "myapp.update_scheduled_notifications"

#     def do(self):
#         print("🔄 Checking scheduled notifications...")
#         logger.info("🔄 Checking scheduled notifications...")

#         notifications = Notification.objects.filter(is_scheduled=True, scheduled_time__lte=now())
#         print(f"🛑 Found {notifications.count()} notifications to unlock")
#         logger.info(f"🛑 Found {notifications.count()} notifications to unlock")

#         for notification in notifications:
#             notification.is_scheduled = False  # ✅ ปลดล็อกให้แจ้งเตือนแสดง
#             notification.save()

#         print(f"✅ Unlocked {notifications.count()} notifications")
#         logger.info(f"✅ Unlocked {notifications.count()} notifications")
