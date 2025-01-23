from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.conf import settings 
from django.utils import timezone

# class Member(AbstractUser):
#     profile = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default_profile_image.png')
#     sex = models.CharField(max_length=10)
#     birthdate = models.DateField(default=date.today)

#     def __str__(self):
#         return self.username


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
    # เชื่อมโยงกับ Member
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ใช้ Custom User Model (Member)
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

PROVINCE_CHOICES = [
    ('choose province', 'เลือกจังหวัด'),
    ('Bangkok', 'Bangkok (กรุงเทพมหานคร)'),
    ('Krabi', 'Krabi (กระบี่)'),
    ('Kanchanaburi', 'Kanchanaburi (กาญจนบุรี)'),
    ('Kalasin', 'Kalasin (กาฬสินธุ์)'),
    ('Kamphaeng Phet', 'Kamphaeng Phet (กำแพงเพชร)'),
    ('Khon Kaen', 'Khon Kaen (ขอนแก่น)'),
    ('Chanthaburi', 'Chanthaburi (จันทบุรี)'),
    ('Chachoengsao', 'Chachoengsao (ฉะเชิงเทรา)'),
    ('Chonburi', 'Chonburi (ชลบุรี)'),
    ('Chainat', 'Chainat (ชัยนาท)'),
    ('Chaiyaphum', 'Chaiyaphum (ชัยภูมิ)'),
    ('Chumphon', 'Chumphon (ชุมพร)'),
    ('Chiang Rai', 'Chiang Rai (เชียงราย)'),
    ('Chiang Mai', 'Chiang Mai (เชียงใหม่)'),
    ('Trang', 'Trang (ตรัง)'),
    ('Trat', 'Trat (ตราด)'),
    ('Tak', 'Tak (ตาก)'),
    ('Nakhon Nayok', 'Nakhon Nayok (นครนายก)'),
    ('Nakhon Pathom', 'Nakhon Pathom (นครปฐม)'),
    ('Nakhon Phanom', 'Nakhon Phanom (นครพนม)'),
    ('Nakhon Ratchasima', 'Nakhon Ratchasima (นครราชสีมา)'),
    ('Nakhon Si Thammarat', 'Nakhon Si Thammarat (นครศรีธรรมราช)'),
    ('Nan', 'Nan (น่าน)'),
    ('Nonthaburi', 'Nonthaburi (นนทบุรี)'),
    ('Narathiwat', 'Narathiwat (นราธิวาส)'),
    ('Phayao', 'Phayao (พะเยา)'),
    ('Prachuap Khiri Khan', 'Prachuap Khiri Khan (ประจวบคีรีขันธ์)'),
    ('Pattani', 'Pattani (ปัตตานี)'),
    ('Phra Nakhon Si Ayutthaya', 'Phra Nakhon Si Ayutthaya (พระนครศรีอยุธยา)'),
    ('Phang Nga', 'Phang Nga (พังงา)'),
    ('Phatthalung', 'Phatthalung (พัทลุง)'),
    ('Phichit', 'Phichit (พิจิตร)'),
    ('Phitsanulok', 'Phitsanulok (พิษณุโลก)'),
    ('Phetchaburi', 'Phetchaburi (เพชรบุรี)'),
    ('Phetchabun', 'Phetchabun (เพชรบูรณ์)'),
    ('Phrae', 'Phrae (แพร่)'),
    ('Phuket', 'Phuket (ภูเก็ต)'),
    ('Maha Sarakham', 'Maha Sarakham (มหาสารคาม)'),
    ('Mukdahan', 'Mukdahan (มุกดาหาร)'),
    ('Mae Hong Son', 'Mae Hong Son (แม่ฮ่องสอน)'),
    ('Yasothon', 'Yasothon (ยโสธร)'),
    ('Yala', 'Yala (ยะลา)'),
    ('Roi Et', 'Roi Et (ร้อยเอ็ด)'),
    ('Ranong', 'Ranong (ระนอง)'),
    ('Rayong', 'Rayong (ระยอง)'),
    ('Ratchaburi', 'Ratchaburi (ราชบุรี)'),
    ('Lopburi', 'Lopburi (ลพบุรี)'),
    ('Lampang', 'Lampang (ลำปาง)'),
    ('Lamphun', 'Lamphun (ลำพูน)'),
    ('Loei', 'Loei (เลย)'),
    ('Sisaket', 'Sisaket (ศรีสะเกษ)'),
    ('Sakon Nakhon', 'Sakon Nakhon (สกลนคร)'),
    ('Songkhla', 'Songkhla (สงขลา)'),
    ('Satun', 'Satun (สตูล)'),
    ('Samut Prakan', 'Samut Prakan (สมุทรปราการ)'),
    ('Samut Songkhram', 'Samut Songkhram (สมุทรสงคราม)'),
    ('Samut Sakhon', 'Samut Sakhon (สมุทรสาคร)'),
    ('Sa Kaeo', 'Sa Kaeo (สระแก้ว)'),
    ('Saraburi', 'Saraburi (สระบุรี)'),
    ('Sing Buri', 'Sing Buri (สิงห์บุรี)'),
    ('Sukhothai', 'Sukhothai (สุโขทัย)'),
    ('Suphan Buri', 'Suphan Buri (สุพรรณบุรี)'),
    ('Surat Thani', 'Surat Thani (สุราษฎร์ธานี)'),
    ('Surin', 'Surin (สุรินทร์)'),
    ('Nong Khai', 'Nong Khai (หนองคาย)'),
    ('Nong Bua Lamphu', 'Nong Bua Lamphu (หนองบัวลำภู)'),
    ('Ang Thong', 'Ang Thong (อ่างทอง)'),
    ('Udon Thani', 'Udon Thani (อุดรธานี)'),
    ('Uttaradit', 'Uttaradit (อุตรดิตถ์)'),
    ('Uthai Thani', 'Uthai Thani (อุทัยธานี)'),
    ('Ubon Ratchathani', 'Ubon Ratchathani (อุบลราชธานี)')
]


class Event(models.Model):
    event_name = models.CharField(max_length=50)
    event_title = models.CharField(max_length=100)
    event_datetime = models.DateTimeField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    province = models.CharField(max_length=100, choices=PROVINCE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now) 
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="events")
    max_participants = models.PositiveIntegerField(default=0)
    # participants = models.ManyToManyField(Member, related_name='events_joined', blank=True)
    

    def __str__(self):
        return self.event_name
    
    class Meta:
        ordering = ['-created_at']


class Event_Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอการตอบกลับ'),
        ('accepted', 'อนุมัติ'),
        ('rejected', 'ปฏิเสธ'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="requests")  
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
        ('request', 'คำขอเข้าร่วมกิจกรรม'),
        ('response', 'ตอบกลับคำขอ'),
        ('other', 'อื่น ๆ'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")  # ผู้รับการแจ้งเตือน
    message = models.TextField()  # ข้อความการแจ้งเตือน
    related_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")  # กิจกรรมที่เกี่ยวข้อง (ถ้ามี)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')  # ประเภทของการแจ้งเตือน
    is_read = models.BooleanField(default=False)  # สถานะว่าอ่านแล้วหรือยัง
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้างการแจ้งเตือน

    def __str__(self):
        return f"การแจ้งเตือนสำหรับ {self.user.username} - {self.notification_type}"
    
    class Meta:
        ordering = ['-created_at']

    def mark_as_read(self):
        """เปลี่ยนสถานะการแจ้งเตือนเป็นอ่านแล้ว"""
        self.is_read = True
        self.save()

    
class ChatRoom(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    users = models.ManyToManyField(Member)

    def __str__(self):
        return f"ChatRoom for {self.event.name}"


class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Member, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chatroom.event.name}"




class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('ความผิดพลาดของระบบ', 'ความผิดพลาดของระบบ'),
        ('พฤติกรรมไม่เหมาะสม', 'พฤติกรรมไม่เหมาะสม'),
        ('Other', 'อื่นๆ'),
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



