from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
# from myapp.models import Notification
from myapp.models import Event, Notification, Event_Request

# def check_and_update_notifications():
#     """ตรวจสอบและปลดล็อกแจ้งเตือนที่ถึงเวลา"""
#     notifications = Notification.objects.filter(is_scheduled=True, scheduled_time__lte=now())
#     for notification in notifications:
#         notification.is_scheduled = False  # ✅ ปลดล็อกให้แจ้งเตือนแสดง
#         notification.save()
    
#     print(f"✅ ปลดล็อก {notifications.count()} การแจ้งเตือนสำเร็จ!")

# def start_scheduler():
#     """เริ่ม Scheduler สำหรับ Windows"""
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(check_and_update_notifications, 'interval', minutes=1)  # ✅ รันทุก 1 นาที
#     scheduler.start()

def check_and_create_notifications():
    """สร้างแจ้งเตือนใหม่สำหรับอีเว้นท์ที่ถึงเวลารีวิว และอัปเดต has_ended=True เพื่อป้องกันแจ้งซ้ำ"""

    # ค้นหาอีเว้นท์ที่ถึงเวลาแล้ว แต่ยังไม่มีการแจ้งเตือนรีวิว
    events = Event.objects.filter(
        event_datetime__lte=now(),  # ✅ อีเว้นท์ที่ถึงเวลาแล้ว
        has_ended=False  # ✅ ต้องยังไม่ถูกแจ้งเตือน
    )

    for event in events:
        # 🔹 ดึงเจ้าของกิจกรรมและผู้เข้าร่วมที่ตอบรับแล้ว
        participants = list(Event_Request.objects.filter(
            event=event, response_status="accepted"
        ).values_list('sender', flat=True))

        recipients = [event.created_by.id] + participants  # ✅ รวมเจ้าของกิจกรรมและผู้เข้าร่วม

        # ✅ ตรวจสอบว่ามีแจ้งเตือนอยู่แล้วหรือยัง
        existing_notification = Notification.objects.filter(related_event=event, notification_type="อื่น ๆ").exists()

        if not existing_notification:  # 🔥 ถ้ายังไม่มี ให้สร้างแจ้งเตือนใหม่
            review_link = f"/event/{event.id}/review/"
            message = f"กิจกรรม {event.event_name} ของคุณเป็นยังไงบ้าง? มารีวิวกันเถอะ! <a href='{review_link}'>คลิกที่นี่</a>"

            for user_id in recipients:
                Notification.objects.create(
                    user_id=user_id,
                    message=message,
                    related_event=event,
                    notification_type="system",
                    is_read=False
                )

            # ✅ ป้องกันแจ้งซ้ำ → อัปเดตว่า Event นี้แจ้งเตือนแล้ว
            event.has_ended = True
            event.save()

            print(f"✅ สร้างแจ้งเตือนรีวิวสำหรับ Event {event.id} และปิดการแจ้งเตือนซ้ำ!")

def start_scheduler():
    """เริ่ม Scheduler ให้ทำงานอัตโนมัติ"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_create_notifications, 'interval', minutes=1)  # ✅ รันทุก 1 นาที
    scheduler.start()