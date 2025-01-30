from django.core.management.base import BaseCommand
from django.utils.timezone import now
from myapp.models import Event, Notification, Event_Request

class Command(BaseCommand):
    help = "Check and send event reminders when event_datetime is reached"

    def handle(self, *args, **kwargs):
        current_time = now()
        events = Event.objects.filter(event_datetime__lte=current_time, is_active=True)

        for event in events:
            # 🔹 ดึงรายชื่อคนที่ได้รับการตอบรับเข้าร่วม
            accepted_requests = Event_Request.objects.filter(event=event, response_status='accepted')

            for request in accepted_requests:
                Notification.objects.create(
                    user=request.sender,  # 🔹 ส่งให้ผู้ที่ได้รับการตอบรับ
                    message=f"กิจกรรม {event.event_name} ได้เริ่มแล้ว! หลังจบอย่าลืมรีวิวเพื่อน ๆ ละ",
                    related_event=event,
                    notification_type="system"
                )

            # 🔹 ปิดสถานะกิจกรรมที่หมดเวลา
            # event.has_ended = True
            # event.save()

        self.stdout.write(self.style.SUCCESS("แจ้งเตือนการรีวิวแล้ว"))
