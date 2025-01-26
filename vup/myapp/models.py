from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.conf import settings 
from django.utils import timezone
from django.utils.timezone import now


class Member(AbstractUser):
    is_banned = models.BooleanField(default=False)
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default_profile_image.png')
    sex = models.CharField(max_length=10)
    birthdate = models.DateField(blank=True, null=True) 
    description = models.CharField(max_length=30, blank=True, null=True,default='เพิ่มคำอธิบายของคุณ')
    
    @property
    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None 
    
    def ban(self):
        self.is_banned = True
        self.save()

    def unban(self):
        self.is_banned = False
        self.save()
    def __str__(self):
        return self.username

class User(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  # เมื่อ Member ถูกลบ, เก็บค่าเป็น NULL
        null=True,
        blank=True
    )

    # คัดลอกข้อมูลจาก Member
    username = models.CharField(max_length=150)
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default_profile_image.png')
    sex = models.CharField(max_length=10, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=30, blank=True, null=True, default='เพิ่มคำอธิบายของคุณ')

    def __str__(self):
        return self.username

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    event_title = models.CharField(max_length=100)
    event_datetime = models.DateTimeField()
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    province = models.CharField(max_length=100,)
    created_at = models.DateTimeField(default=timezone.now) 
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="events")
    max_participants = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # is_banned = models.BooleanField(default=False)
    # participants = models.ManyToManyField(Member, related_name='events_joined', blank=True)
    

    def __str__(self):
        return self.event_name
    
    @property
    def time_since(self):
        delta = now() - self.created_at
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return "ตอนนี้"
        elif seconds < 3600:
            return f"{seconds // 60} นาที"
        elif seconds < 86400:
            return f"{seconds // 3600} ชั่วโมง"
        elif seconds < 31536000:
            return f"{seconds // 86400} วัน"
        else:
            return f"{seconds // 31536000} ปี"
    
    class Meta:
        ordering = ['-created_at']


class Event_Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอการตอบกลับ'),
        ('accepted', 'อนุมัติ'),
        ('rejected', 'ปฏิเสธ'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_requests")
    sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="sent_requests")  
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="received_requests")  
    request_time = models.DateTimeField(auto_now_add=True) 
    response_status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='pending',)

    class Meta:
        indexes = [models.Index(fields=['event', 'receiver', 'response_status']),]

    def __str__(self):
        return f"Request by {self.sender} to join {self.event} - Status: {self.response_status}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('คำขอเข้าร่วมกิจกรรม', 'คำขอเข้าร่วมกิจกรรม'),
        ('ตอบกลับคำขอ', 'ตอบกลับคำขอ'),
        ('อื่น ๆ', 'อื่น ๆ'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")  # ผู้รับการแจ้งเตือน
    message = models.TextField()  # ข้อความการแจ้งเตือน
    related_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")  # กิจกรรมที่เกี่ยวข้อง (ถ้ามี)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')  # ประเภทของการแจ้งเตือน
    is_read = models.BooleanField(default=False)  # สถานะว่าอ่านแล้วหรือยัง
    # is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้างการแจ้งเตือน
    related_request = models.ForeignKey(
        'Event_Request',  # เพิ่มความสัมพันธ์กับ Event_Request
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"การแจ้งเตือนสำหรับ {self.user.username} - {self.notification_type}"
    
    class Meta:
        ordering = ['-created_at']

    def mark_as_read(self):
        """เปลี่ยนสถานะการแจ้งเตือนเป็นอ่านแล้ว"""
        self.is_read = True
        self.save()

    @property
    def is_event_active(self):
        """ตรวจสอบว่าอีเว้นท์ที่เกี่ยวข้องยัง Active อยู่หรือไม่"""
        if self.related_event:
            return self.related_event.is_active
        return False  # ถ้าไม่มีอีเว้นท์ที่เกี่ยวข้อง

    
class ChatRoom(models.Model):
    name = models.CharField(max_length=100, default='Unnamed Chat Room')   # ชื่อห้องแชท
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='chat_rooms')  # เชื่อมกับ Event
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms', blank=True)  # สมาชิกในห้องแชท
    created_at = models.DateTimeField(default=timezone.now) 
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_chat_rooms")  # ใช้ Member
    is_active = models.BooleanField(default=True)

    @property
    def name(self):
        # ดึงชื่อห้องแชทจาก event.event_name
        return self.event.event_name

    @name.setter
    def name(self, value):
        # อัปเดต event.event_name
        self.event.event_name = value
        self.event.save()

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()

    def member_count(self):
        return self.members.count()

    
class Chat_Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Member, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Message from {self.sender.username} in {self.chatroom.event.name}"
    def __str__(self):
        return f"{self.sender.username} : {self.message}"
    
    class Meta:
        ordering = ['-created_at']


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('ความผิดพลาดของระบบ', 'ความผิดพลาดของระบบ'),
        ('พฤติกรรมไม่เหมาะสม', 'พฤติกรรมไม่เหมาะสม'),
        ('อื่นๆ', 'อื่นๆ'),
    ]

    STATUS_CHOICES = [
        ('รอดำเนินการ', 'รอดำเนินการ'),
        ('เตือนผู้ใช้งาน', 'เตือนผู้ใช้งาน'),
        ('ปฏิเสธการรายงาน', 'ปฏิเสธการรายงาน'),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made',verbose_name="ผู้รายงาน")
    event_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events_owned',verbose_name="เจ้าของอีเวนต์",null=True,blank=True)   
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='reported_events',verbose_name="อีเว้นที่ถูกรายงาน")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES,null=True, verbose_name="ประเภทการรายงาน")
    description = models.TextField(blank=True, null=True, verbose_name="คำอธิบาย")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่รายงาน")
    # warning_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนการแจ้งเตือน")
    is_warned = models.CharField(max_length=15,choices=STATUS_CHOICES,default='รอดำเนินการ',verbose_name="สถานะการแจ้งเตือน")

    def __str__(self):
        return f"{self.reporter.username} รายงานกิจกรรม {self.event.event_name}"

    @classmethod
    def count_reports_by_event(cls, event):
        return cls.objects.filter(event=event).count()

    @classmethod
    def count_warnings_by_event(cls, event):
        return cls.objects.filter(event=event, is_warned='เตือน').count()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "รายงาน"
        verbose_name_plural = "รายงานทั้งหมด"



