from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm



class MemberRegistrationForm(UserCreationForm):

    SEX_CHOICES = [
        ('', 'เลือก'),
        ('ชาย', 'ชาย'),
        ('หญิง', 'หญิง'),
    ]

    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.Select, required=True)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Member
        fields = ('profile', 'username', 'email', 'first_name', 'last_name', 'sex', 'birthdate', 'password1', 'password2')

class MemberUpdateForm(forms.ModelForm):
    
    SEX_CHOICES = [
        ('', 'เลือก'),
        ('ชาย', 'ชาย'),
        ('หญิง', 'หญิง'),
    ]

    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.Select, required=True)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Member
        fields = ('profile', 'username', 'email', 'first_name', 'last_name', 'sex', 'birthdate', 'description')
        widgets = {
            # 'profile': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'profile': forms.ClearableFileInput(attrs={'class': 'form-input', 'clear': False}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MemberUpdateForm, self).__init__(*args, **kwargs)
        # ตั้งค่า default ค่าของ sex และ birthdate จากข้อมูลในฐานข้อมูล (หากมีค่า)
        if self.instance.pk:
            self.fields['sex'].initial = self.instance.sex  # ค่าเริ่มต้นสำหรับ sex
            self.fields['birthdate'].initial = self.instance.birthdate  # ค่าเริ่มต้นสำหรับ birthdate

PROVINCE_CHOICES = [
    ('เลือกจังหวัด', 'เลือกจังหวัด'),
    ('กรุงเทพมหานคร', 'กรุงเทพมหานคร'),
    ('กระบี่', 'กระบี่'),
    ('กาญจนบุรี', 'กาญจนบุรี'),
    ('กาฬสินธุ์', 'กาฬสินธุ์'),
    ('กำแพงเพชร', 'กำแพงเพชร'),
    ('ขอนแก่น', 'ขอนแก่น'),
    ('จันทบุรี', 'จันทบุรี'),
    ('ฉะเชิงเทรา', 'ฉะเชิงเทรา'),
    ('ชลบุรี', 'ชลบุรี'),
    ('ชัยนาท', 'ชัยนาท'),
    ('ชัยภูมิ', 'ชัยภูมิ'),
    ('ชุมพร', 'ชุมพร'),
    ('เชียงราย', 'เชียงราย'),
    ('เชียงใหม่', 'เชียงใหม่'),
    ('ตรัง', 'ตรัง'),
    ('ตราด', 'ตราด'),
    ('ตาก', 'ตาก'),
    ('นครนายก', 'นครนายก'),
    ('นครปฐม', 'นครปฐม'),
    ('นครพนม', 'นครพนม'),
    ('นครราชสีมา', 'นครราชสีมา'),
    ('นครศรีธรรมราช', 'นครศรีธรรมราช'),
    ('นครสวรรค์', 'นครสวรรค์'),
    ('นนทบุรี', 'นนทบุรี'),
    ('นราธิวาส', 'นราธิวาส'),
    ('น่าน', 'น่าน'),
    ('บึงกาฬ', 'บึงกาฬ'),
    ('บุรีรัมย์', 'บุรีรัมย์'),
    ('ปทุมธานี', 'ปทุมธานี'),
    ('ประจวบคีรีขันธ์', 'ประจวบคีรีขันธ์'),
    ('ปราจีนบุรี', 'ปราจีนบุรี'),
    ('ปัตตานี', 'ปัตตานี'),
    ('พะเยา', 'พะเยา'),
    ('พระนครศรีอยุธยา', 'พระนครศรีอยุธยา'),
    ('พังงา', 'พังงา'),
    ('พัทลุง', 'พัทลุง'),
    ('พิจิตร', 'พิจิตร'),
    ('พิษณุโลก', 'พิษณุโลก'),
    ('เพชรบุรี', 'เพชรบุรี'),
    ('เพชรบูรณ์', 'เพชรบูรณ์'),
    ('แพร่', 'แพร่'),
    ('ภูเก็ต', 'ภูเก็ต'),
    ('มหาสารคาม', 'มหาสารคาม'),
    ('มุกดาหาร', 'มุกดาหาร'),
    ('แม่ฮ่องสอน', 'แม่ฮ่องสอน'),
    ('ยโสธร', 'ยโสธร'),
    ('ยะลา', 'ยะลา'),
    ('ร้อยเอ็ด', 'ร้อยเอ็ด'),
    ('ระนอง', 'ระนอง'),
    ('ระยอง', 'ระยอง'),
    ('ราชบุรี', 'ราชบุรี'),
    ('ลพบุรี', 'ลพบุรี'),
    ('ลำปาง', 'ลำปาง'),
    ('ลำพูน', 'ลำพูน'),
    ('เลย', 'เลย'),
    ('ศรีสะเกษ', 'ศรีสะเกษ'),
    ('สกลนคร', 'สกลนคร'),
    ('สงขลา', 'สงขลา'),
    ('สตูล', 'สตูล'),
    ('สมุทรปราการ', 'สมุทรปราการ'),
    ('สมุทรสงคราม', 'สมุทรสงคราม'),
    ('สมุทรสาคร', 'สมุทรสาคร'),
    ('สระแก้ว', 'สระแก้ว'),
    ('สระบุรี', 'สระบุรี'),
    ('สิงห์บุรี', 'สิงห์บุรี'),
    ('สุโขทัย', 'สุโขทัย'),
    ('สุพรรณบุรี', 'สุพรรณบุรี'),
    ('สุราษฎร์ธานี', 'สุราษฎร์ธานี'),
    ('สุรินทร์', 'สุรินทร์'),
    ('หนองคาย', 'หนองคาย'),
    ('หนองบัวลำภู', 'หนองบัวลำภู'),
    ('อ่างทอง', 'อ่างทอง'),
    ('อำนาจเจริญ', 'อำนาจเจริญ'),
    ('อุดรธานี', 'อุดรธานี'),
    ('อุตรดิตถ์', 'อุตรดิตถ์'),
    ('อุทัยธานี', 'อุทัยธานี'),
    ('อุบลราชธานี', 'อุบลราชธานี'),
]

CATEGORY_CHOICES = [
    ('เลือกหมวด', 'เลือกหมวด'),
    ('การศึกษา', 'การศึกษา'),
    ('กีฬา', 'กีฬา'),
    ('ท่องเที่ยว', 'ท่องเที่ยว'),
    ('อาหาร', 'อาหาร'),
    ('ศิลปะ', 'ศิลปะ'),
    ('สุขภาพ', 'สุขภาพ'),
    ('ความบันเทิง', 'ความบันเทิง')
    
]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'event_title', 'event_datetime', 'location', 'category', 'max_participants', 'province']

        labels = {
            'event_name': 'ชื่อกิจกรรม',
            'event_title': 'รายละเอียด',
            'event_datetime': 'วันที่ทำกิจกรรม',
            'location': 'สถานที่',
            'category': 'หมวดหมู่',
            'max_participants': 'จำนวนผู้เข้าร่วมสูงสุด',
            'province': 'จังหวัด',
        }

        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อกิจกรรม'}),
            'event_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'รายละเอียด'}),
            'event_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), 
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สถานที่'}),
            'category': forms.Select(choices=CATEGORY_CHOICES, attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'จำนวนผู้เข้าร่วมสูงสุด', 'min': '1'}),
            'province': forms.Select(choices=PROVINCE_CHOICES, attrs={'class': 'form-control'}),
        }

class UpdateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'event_title', 'event_datetime', 'location', 'category', 'max_participants', 'province']

        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}),
            'event_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'event_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'category': forms.Select(choices=CATEGORY_CHOICES, attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Participants', 'min': '1'}),
            'province': forms.Select(choices=PROVINCE_CHOICES, attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_name'].required = False
        self.fields['event_title'].required = False

# class EventReviewForm(forms.ModelForm):
#     class Meta:
#         model = Event_Review
#         fields = ['attendance_status', 'comment']

class EventReviewForm(forms.ModelForm):
    class Meta:
        model = Event_Review
        fields = ['attendance_status', 'comment']
        widgets = {
            'attendance_status': forms.RadioSelect(attrs={'class': 'form-control'}),  # ใช้ Radio Select สำหรับสถานะ
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  
                'placeholder': 'กรอกความคิดเห็นของคุณที่นี่'  
            }),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'คำอธิบาย...'}),
        }
        labels = {
            'report_type': 'Type of Report',
            'description': 'Description',
        }

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = Chat_Message
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={
                'class': 'chat-input',
                'placeholder': 'Type a message...',
                'autocomplete': 'off'
            }),
        }

