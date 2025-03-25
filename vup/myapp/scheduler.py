from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now, timedelta
from myapp.models import Event, Notification, Event_Request

def check_and_create_notifications():
    """สร้างแจ้งเตือนใหม่สำหรับอีเว้นท์ที่ถึงเวลารีวิว และอัปเดต has_ended=True เพื่อป้องกันแจ้งซ้ำ"""
    
    # ค้นหาอีเว้นท์ที่ถึงเวลาแล้ว แต่ยังไม่มีการแจ้งเตือนรีวิว
    events = Event.objects.filter(
        event_datetime__lte=now(), 
        has_ended=False  
    )

    for event in events:
        # คำนวณเวลา 24 ชั่วโมง 
        notification_time = event.event_datetime + timedelta(hours=24)  

        # ตรวจสอบว่าถึงเวลาที่กำหนดสำหรับการแจ้งเตือนหรือยัง
        if now() >= notification_time:
            participants = list(Event_Request.objects.filter(
                event=event, response_status="accepted"
            ).values_list('sender', flat=True))

            recipients = [event.created_by.id] + participants 

            # ตรวจสอบการแจ้งเตือนที่เกี่ยวข้อง
            existing_notification = Notification.objects.filter(related_event=event, notification_type="อื่น ๆ").exists()

            if not existing_notification:  
                review_link = f"/event/{event.id}/review/"
                message = f"กิจกรรม '{event.event_name}' ของคุณเป็นยังไงบ้าง? มารีวิวกันเถอะ! <a href='{review_link}'>คลิกที่นี่</a>"

                for user_id in recipients:
                    Notification.objects.create(
                        user_id=user_id,
                        message=message,
                        related_event=event,
                        notification_type="system",
                        is_read=False
                    )

                # อัปเดตสถานะของกิจกรรมว่าเสร็จสิ้นแล้ว
                event.has_ended = True
                event.save()

                print(f"✅ สร้างแจ้งเตือนรีวิวสำหรับ Event {event.id} และปิดการแจ้งเตือนซ้ำ!")

def start_scheduler():
    """เริ่ม Scheduler ให้ทำงานอัตโนมัติ"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_create_notifications, 'interval', minutes=1) 
    scheduler.start()



# def check_and_create_notifications():
#     """สร้างแจ้งเตือนใหม่สำหรับอีเว้นท์ที่ถึงเวลารีวิว และอัปเดต has_ended=True เพื่อป้องกันแจ้งซ้ำ"""

#     # ค้นหาอีเว้นท์ที่ถึงเวลาแล้ว แต่ยังไม่มีการแจ้งเตือนรีวิว
#     events = Event.objects.filter(
#         event_datetime__lte=now(), 
#         has_ended=False  
#     )

#     for event in events:
#         participants = list(Event_Request.objects.filter(
#             event=event, response_status="accepted"
#         ).values_list('sender', flat=True))

#         recipients = [event.created_by.id] + participants 

#         existing_notification = Notification.objects.filter(related_event=event, notification_type="อื่น ๆ").exists()

#         if not existing_notification:  
#             review_link = f"/event/{event.id}/review/"
#             message = f"กิจกรรม '{event.event_name}' ของคุณเป็นยังไงบ้าง? มารีวิวกันเถอะ! <a href='{review_link}'>คลิกที่นี่</a>"

#             for user_id in recipients:
#                 Notification.objects.create(
#                     user_id=user_id,
#                     message=message,
#                     related_event=event,
#                     notification_type="system",
#                     is_read=False
#                 )

#             event.has_ended = True
#             event.save()

#             print(f"✅ สร้างแจ้งเตือนรีวิวสำหรับ Event {event.id} และปิดการแจ้งเตือนซ้ำ!")