from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *


class MemberRegistrationForm(UserCreationForm):

    SEX_CHOICES = [
        ('', 'Select'),
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.Select, required=True)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Member
        fields = ('profile', 'username', 'email', 'first_name', 'last_name', 'sex', 'birthdate', 'password1', 'password2')

class MemberUpdateForm(forms.ModelForm):
    SEX_CHOICES = [
        ('', 'Select'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.Select, required=True)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Member
        fields = ('profile', 'username', 'email', 'first_name', 'last_name', 'sex', 'birthdate', 'description')
        widgets = {
            'profile': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Add a description...'}),
        }



# List ของ 77 จังหวัดในประเทศไทย
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

CATEGORY_CHOICES = [
    ('food', 'Food'),
    ('travel', 'Travel'),
    ('game', 'Game'),
    ('sport', 'Sport'),
    ('music', 'Music'),
    ('art', 'Art'),
    ('education', 'Education'),
    # เพิ่มตัวเลือกอื่นๆ ที่ต้องการ
]

class EventForm(forms.ModelForm):
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