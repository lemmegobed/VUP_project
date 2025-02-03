from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
from myapp.models import Notification

def check_and_update_notifications():
    """ตรวจสอบและปลดล็อกแจ้งเตือนที่ถึงเวลา"""
    notifications = Notification.objects.filter(is_scheduled=True, scheduled_time__lte=now())
    for notification in notifications:
        notification.is_scheduled = False  # ✅ ปลดล็อกให้แจ้งเตือนแสดง
        notification.save()
    
    print(f"✅ ปลดล็อก {notifications.count()} การแจ้งเตือนสำเร็จ!")

def start_scheduler():
    """เริ่ม Scheduler สำหรับ Windows"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_update_notifications, 'interval', minutes=1)  # ✅ รันทุก 1 นาที
    scheduler.start()
