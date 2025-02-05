from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils.timesince import timesince
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
# from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now, timedelta
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .serializers import ChatMessageSerializer
# from django.core.management.base import BaseCommand
from django.urls import reverse



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_banned:  
                    # เพิ่มข้อความเพียงครั้งเดียว
                    form.add_error(None, 'บัญชีของคุณถูกระงับ โปรดติดต่อผู้ดูแลระบบ')
                else:
                    login(request, user)
                    return redirect('dashboard' if user.is_superuser else 'feed')
            else:
                form.add_error(None, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.method == "POST":
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = MemberRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@receiver(post_save, sender=Member)
def create_or_update_user(sender, instance, created, **kwargs):
    if created:
        # สร้าง User ใหม่เมื่อ Member ถูกสร้าง
        User.objects.create(
            member=instance,
            username=instance.username,
            profile=instance.profile,
            sex=instance.sex,
            birthdate=instance.birthdate,
            description=instance.description
        )
    else:
        # อัปเดต User ที่เกี่ยวข้องเมื่อ Member ถูกแก้ไข
        user = User.objects.filter(member=instance).first()
        if user:
            user.username = instance.username
            user.profile = instance.profile
            user.sex = instance.sex
            user.birthdate = instance.birthdate
            user.description = instance.description
            user.save()




def upload_ads(request):
    if not request.user.is_superuser:  
        return redirect('feed')

    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            if Advertisement.objects.count() < 5:  
                form.save()
            return redirect('upload_ads')  
    else:
        form = AdvertisementForm()

    advertisements = Advertisement.objects.all()
    return render(request, 'admin/upload_ads.html', {'form': form, 'advertisements': advertisements})

def show_ads(request):
    advertisements = Advertisement.objects.all()
    events = Event.objects.all()
    return render(request, 'member/feed.html', {'advertisements': advertisements, 'events': events})

# @staff_member_required
def admin_dashboard(request):

    members = Member.objects.filter(is_banned=False,is_superuser=False)
    total_members = members.count()

    users = Member.objects.all()
    total_users = users.count()
    total_delete_member = total_users - total_members

    male_members = Member.objects.filter(sex='M').count() 
    female_members = Member.objects.filter(sex='F').count()  

    reports = Report.objects.all()
    total_warned_event = reports.filter(is_warned='เตือน').count()
    report_event_by_category = Report.objects.values('report_type').annotate(report_event_by_category=Count('id')).order_by('report_type')
    
    total_events = Event.objects.count()
    events_by_category = Event.objects.values('category').annotate(event_count=Count('id'))

    recent_events = Event.objects.order_by('-event_datetime')[:5]

    context = {
        'total_members': total_members,
        'total_users': total_users,
        'total_delete_member':total_delete_member,
        'male_members': male_members,
        'female_members': female_members,
        'total_events': total_events,
        'events_by_category': events_by_category,
        'recent_events': recent_events,
        'users': users,  
        'members': members,  
        'reports': reports,  
        'total_warned_event': total_warned_event,  
        'report_event_by_category':report_event_by_category,
        }
    return render(request, 'admin/dashboard.html',context)

def userdata_admin(request):
    members = Member.objects.filter(is_banned=False,is_superuser=False)
    members = members.annotate(activity_count=Count('events'))  
    total_members = members.count()  

    users = Member.objects.all()
    total_users = users.count()

    total_banned_member = total_users - total_members

    male_members = members.filter(sex='M').count() 
    female_members = members.filter(sex='F').count()

    total_events = Event.objects.count()
    events_by_category = Event.objects.values('category').annotate(event_count=Count('id'))

    context = {
        'total_members': total_members,       
        'male_members': male_members,         
        'female_members': female_members,     
        'total_users': total_users,          
        'total_events': total_events,         
        'events_by_category': events_by_category,  
        'total_banned_member': total_banned_member, 
        'members': members,                   
        'users': users,                       
    }
    return render(request, 'admin/userdata_admin.html', context)


def block_user(request, id):
    if request.method == 'POST':
        try:
            # ตรวจสอบว่ามีผู้ใช้ในระบบหรือไม่
            member = get_object_or_404(Member, id=id)
            member.is_banned = True  # เปลี่ยนสถานะผู้ใช้เป็น "ถูกแบน"
            member.is_active = False 
            member.save()
            return JsonResponse({'status': 'success', 'message': f'{member.username} ถูกแบนแล้ว'})
        except Exception as e:
            # จับข้อผิดพลาดและส่งข้อความกลับ
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def warn_event(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    report.is_warned = True
    report.save()

    messages.success(request, f"Warning sent for event '{report.event.event_name}'.")
    return redirect('report_admin')

def edit_member(request, member_id):
    # member_data = Member.objects.get(username=request.user.username) 
    member_data = get_object_or_404(Member, id=member_id)  

    if request.method == 'POST':
        # form = MemberUpdateForm(request.POST, request.FILES, instance=member)
        form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
        if form.is_valid():
            form.save()  # บันทึกข้อมูลใหม่
            return redirect('userdata')  # เปลี่ยนเส้นทางหลังจากแก้ไขเสร็จ
    else:
        form = MemberUpdateForm(instance=member_data)  # โหลดข้อมูลเดิมในแบบฟอร์ม

    context = {
        'form': form,
        'member_data': member_data,
    }
    return render(request, 'admin/edit_member.html', context)

def report_admin(request):
    reports = Report.objects.all()

    waiting_reports = reports.filter(is_warned='รอดำเนินการ')

    unique_reports = waiting_reports.values('event', 'report_type').distinct()

    total_reports = reports.count()
    total_waiting = unique_reports.count()  # นับเฉพาะการเตือนที่ไม่ซ้ำ
    total_warned = reports.filter(is_warned='เตือน').count()
    total_rejected = reports.filter(is_warned='ปฏิเสธการรายงาน').count()

    # นับประเภทการรายงาน (เฉพาะรอดำเนินการ)
    system_issues = unique_reports.filter(report_type='ความผิดพลาดของระบบ').count()
    inappropriate_behavior = unique_reports.filter(report_type='พฤติกรรมไม่เหมาะสม').count()
    other_issues = unique_reports.filter(report_type='Other').count()

    return render(request, 'admin/report_admin.html', {
        'total_reports': total_reports,         # รายงานทั้งหมด
        'total_waiting': total_waiting,         # รอดำเนินการ (ไม่ซ้ำ)
        'total_warned': total_warned,           # รายงานที่เตือนแล้ว
        'total_rejected': total_rejected,       # รายงานที่ปฏิเสธแล้ว
        'system_issues': system_issues,         # ปัญหาของระบบ
        'inappropriate_behavior': inappropriate_behavior,  # พฤติกรรมไม่เหมาะสม
        'other_issues': other_issues,           # อื่น ๆ
        'waiting_reports': waiting_reports,     # รายงานที่ยังรอดำเนินการ
    })

def event_detail_report(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    reports = Report.objects.filter(event=event)

    if request.method == "POST":
        action = request.POST.get("action")  

        if action == "warn":
            # ตรวจสอบว่ามีรายงานหรือไม่
            if reports.exists():
                reports.update(is_warned="เตือน")

                event.is_active = False
                event.save()

                Notification.objects.create(
                    user=event.created_by,  # ผู้สร้างอีเว้นท์
                    message=f"กิจกรรม '{event.event_name}' ของคุณถูกลบเนื่องจากละเมิดกฎชุมชน",  # ข้อความการแจ้งเตือน
                    notification_type="system",  # ประเภทของการแจ้งเตือน
                    related_event=event  # เชื่อมโยงกับอีเว้นท์ที่เกี่ยวข้อง
                )

                messages.success(request, f"The event '{event.event_name}' has been warned and hidden.")
            else:
                messages.error(request, "No reports found for this event.")

        elif action == "reject":
            if reports.exists():
                reports.update(is_warned="ปฏิเสธการรายงาน")
                messages.success(request, f"The report for the event '{event.event_name}' has been rejected.")
            else:
                messages.error(request, "No reports found for this event.")

        return redirect('report_admin')
    
    context = {
            'event': event,
            'reports': reports,
    }

    return render(request, 'admin/event_report_detail.html', context)


def submit_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not hasattr(event, 'created_by') or event.created_by is None:
        messages.error(request, "Event does not have an owner. Cannot submit report.")
        return redirect('feed')

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.event = event
            report.event_owner = event.created_by  # ใช้ event.created_by อย่างปลอดภัย
            report.save()
            messages.success(request, "Your report has been submitted successfully.")
            return redirect('feed')
    else:
        form = ReportForm()

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'member/event/submit_report.html', context)



@login_required
def home_view(request):

    events = Event.objects.filter(
        is_active=True,                # กรองเฉพาะอีเว้นท์ที่ยัง active
        created_by__is_banned=False,  # เจ้าของอีเว้นท์ไม่ถูกแบน
        created_by__is_active=True    # เจ้าของอีเว้นท์ยัง active
    ).select_related('created_by')

    # ดึงข้อมูลผู้ใช้ปัจจุบัน
    form = EventForm()
    current_user = request.user
    member_data = Member.objects.get(username=current_user.username)

    # ส่งข้อมูลไปยัง Template
    return render(request, 'member/feed.html', {
        'member_data': member_data,
        'form': form,
        'events': events
    })


PROVINCES = [
    "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา",
    "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก",
    "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน",
    "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พังงา",
    "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "พะเยา", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร",
    "แม่ฮ่องสอน", "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน",
    "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว",
    "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู",
    "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"
]

@login_required
def profile_view(request):
    member_data = Member.objects.get(username=request.user.username) 
    
    # ดึงกิจกรรมที่ผู้ใช้สร้าง
    events = Event.objects.filter(created_by=request.user, is_active=True)
    total_events = events.count()

    total_joined_events = Event_Request.objects.filter(sender=member_data, response_status='accepted').count()

    # ดึงกิจกรรมที่กำลังดำเนินการอยู่ (ข้อมูลจาก my_activity)
    # active_events = Event.objects.filter(created_by=request.user, is_active=True)
    # active_events_count = active_events.count()

    # ฟอร์มแก้ไขโปรไฟล์
    if request.method == 'POST':
        if 'update_profile' in request.POST:  # ตรวจสอบว่ามาจากการอัปเดตโปรไฟล์
            form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
            if form.is_valid():
                form.save()  
                return redirect('profile')  

        elif 'event_submit' in request.POST:  # ตรวจสอบว่ามาจากการสร้างหรือแก้ไขกิจกรรม
            event_id = request.POST.get('event_id', None)
            if event_id:  
                event = get_object_or_404(Event, id=event_id, created_by=request.user)
                event_form = EventForm(request.POST, instance=event)
            else:  
                event_form = EventForm(request.POST)
                event_form.instance.created_by = request.user

            if event_form.is_valid():
                event_form.save()
                return redirect('profile')

    else:
        form = MemberUpdateForm(instance=member_data)  
        event_form = EventForm()  

    context = {
        'member_data': member_data,
        'events': events,
        'total_events': total_events,  
        'total_joined_events':total_joined_events,
        # 'active_events': active_events,  
        # 'active_events_count': active_events_count,
        'form': form,
        'event_form': event_form,  # ฟอร์มสร้าง/แก้ไขกิจกรรม
        "provinces": PROVINCES
    }
    return render(request, 'member/profile.html', context)


# เช็คในลงทะเบียน
def check_username_register(request):
    username = request.GET.get("username", None)
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})

# เช็คในฟอร์ม
@login_required
def check_username(request):
    username = request.GET.get("username", None)
    
    if username == request.user.username:
        return JsonResponse({"exists": False})  

    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})

def member_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    user_login = Member.objects.get(username=request.user.username)

    events = Event.objects.filter(created_by=member, is_active=True)
    total_events = events.count()

    total_joined_events = Event_Request.objects.filter(sender=member, response_status='accepted').count()

    context = {
        'user_login':user_login,
        'member': member,
        'events':events,
        'total_events':total_events,
        'total_joined_events': total_joined_events,
        
    } 
    return render(request, 'member/member_profile.html', context)

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()  
        return redirect('profile')  

# def profile_view(request):
#     member_data = Member.objects.get(username=request.user.username) 
#     user_events = Event.objects.filter(created_by=request.user)  # ดึง Event ที่ผู้ใช้นี้สร้าง
#     total_events = user_events.count()
    
#     if request.method == 'POST':
#         form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
#         if form.is_valid():
#             form.save()  
#             return redirect('profile')  
#     else:
#         form = MemberUpdateForm(instance=member_data)  # กรณีไม่ใช่ POST ให้สร้างฟอร์มจากข้อมูลผู้ใช้ที่ล็อกอิน
    
#     context = {
#         'user_events': user_events,
#         'total_events': total_events,  
#         'form': form,
#         'member_data': member_data
#     }
#     return render(request, 'member/profile.html', context)



    

    
def chat_rooms_list(request):
    # ดึงข้อมูลของผู้ใช้
    member_data = Member.objects.get(username=request.user.username)
    user = request.user

    # ดึงห้องแชทที่เกี่ยวข้องกับผู้ใช้ (ผู้สร้างหรือเป็นสมาชิก)
    chat_rooms = ChatRoom.objects.filter(
        Q(created_by=user) | Q(members=user),  # ผู้ใช้เป็นเจ้าของ หรือเป็นสมาชิกในห้อง
        event__is_active=True,              # อีเว้นต์ต้อง active
        # event__eventrequest__member=user
    ).distinct().order_by('-updated_at')  # เรียงลำดับตาม updated_at จากล่าสุดไปเก่าสุด

    # ส่ง context ให้ template
    context = {
        'member_data': member_data,
        'chat_rooms': chat_rooms,
    }

    return render(request, 'member/chat/chat.html', context)



@login_required
def chat_room_detail(request, chat_room_id):
    member_data = Member.objects.get(username=request.user.username)
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    messages = Chat_Message.objects.filter(chatroom=chat_room).order_by('created_at')

    return render(request, 'member/chat/chat_room_detail.html', {
        'chat_room': chat_room,
        'messages': messages,
        'member_data': member_data,
    })

# ออกจากแชท = กิจกรรม
@login_required

def leave_chat(request, chat_room_id):

    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)

    chat_room.members.remove(request.user)  

    Chat_Message.objects.create(
        chatroom=chat_room,  
        sender=None, 
        message=f"{request.user.username} ได้ออกจากกิจกรรม '{chat_room.event.event_name}'แล้ว", 
        created_at=now(),  
        is_system_message=True,  
    )
    return JsonResponse({"status": "success"})

# def leave_chat(request, chat_room_id):
#     chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
#     chat_room.members.remove(request.user)  # ลบสมาชิกออกจากห้อง
#     return JsonResponse({"status": "success"})

@receiver(post_save, sender=Event)
def update_chatroom_name(sender, instance, **kwargs):
    # อัปเดตชื่อห้องแชทเมื่อ Event ถูกบันทึก
    chat_rooms = ChatRoom.objects.filter(event=instance)
    for chat_room in chat_rooms:
        chat_room.event_name = instance.event_name  # ตั้งชื่อห้องแชทให้ตรงกับ Event
        chat_room.save()

def my_activity(request):
    events = Event.objects.filter(created_by=request.user, is_active=True)
    member_data = Member.objects.get(username=request.user.username) 
    form = EventForm()  
    total_events = events.count()

    if request.method == 'POST':
        if 'event_submit' in request.POST:
            event_id = request.POST.get('event_id', None)
            if event_id:  
                event = get_object_or_404(Event, id=event_id, created_by=request.user)
                form = EventForm(request.POST, instance=event)
            else:  
                form = EventForm(request.POST)
                form.instance.created_by = request.user

            if form.is_valid():
                form.save()
                return redirect('my_activity')

        elif 'delete_event' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id, created_by=request.user)
            event.delete()
            return redirect('my_activity')

    context = {
        'events': events,
        'form': form,
        'member_data': member_data,
        'total_events': total_events,
    }
    return render(request, 'member/my_activity.html', context)


def update_event(request):
    member_data = Member.objects.get(username=request.user.username)
    
    # ดึงกิจกรรมที่ผู้ใช้สร้าง
    events = Event.objects.filter(created_by=request.user)

    if request.method == 'POST':
        # ตรวจสอบว่ามีการส่งข้อมูลฟอร์มเพื่ออัปเดตกิจกรรมหรือไม่
        event_id = request.POST.get('event_id')  # รับค่า id ของกิจกรรมที่ต้องการแก้ไข
        if event_id:
            event = Event.objects.get(id=event_id)  # ดึงกิจกรรมตาม id ที่เลือก
            form = EventForm(request.POST, request.FILES, instance=event)  # ผูกฟอร์มกับข้อมูลเดิม
        else:
            form = EventForm(request.POST, request.FILES)  # ฟอร์มเปล่าหากเป็นการสร้างกิจกรรมใหม่
        
        if form.is_valid():
            form.save()  # อัปเดตกิจกรรมหรือสร้างกิจกรรมใหม่

            ChatRoom.objects.filter(event=event).update(name=event.event_name)
            return redirect('my_activity')  # เมื่อบันทึกแล้วจะกลับไปที่หน้า profile
    else:
        event_id = request.GET.get('event_id')  # รับค่าจาก URL query string สำหรับการแก้ไข
        if event_id:
            event = Event.objects.get(id=event_id)  # ดึงข้อมูลกิจกรรมตาม id
            form = EventForm(instance=event)  # แสดงข้อมูลเก่าในฟอร์ม
        else:
            form = EventForm()  # ฟอร์มเปล่าในการสร้างกิจกรรมใหม่

    return render(request, 'member/my_activity.html', {
        'form': form,
        'member_data': member_data,
        'events': events,
    })


# สร้างอีเว้น
@login_required
def new_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

            #สร้างแจ้งเตือนหลังจากสร้าง
            create_event_notifications(event)  

            #ChatRoom
            chat_room = ChatRoom.objects.create(
                name=event.event_name,
                event=event,
                created_by=request.user
            )
            chat_room.members.add(request.user)  

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = EventForm()
    return render(request, 'member/home.html', {'form': form})


# def new_event_view(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)  
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.created_by = request.user  
#             event.save() 

#             return JsonResponse({'success': True})  
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors})  

#     else:
#         form = EventForm() 
#     return render(request, 'member/home.html', {'form': form})


# def edit_event(request, event_id):
#     event = get_object_or_404(Event, id=event_id)


#     if request.method == 'POST':
#         form = EventForm(request.POST, instance=event)
#         if form.is_valid():
#             form.save()  # บันทึกการเปลี่ยนแปลง
#             return redirect('feed', event_id=event.id)  # ไปที่หน้ารายละเอียด event
#     else:
#         form = EventForm(instance=event)  # แสดงฟอร์มที่มีข้อมูลจาก event เดิม

#     return render(request, 'member/feed.html', {'form': form, 'events': events})

#ลบอีเว้น-ผู้ใช้

 
# ค้นหาอีเว้น
def search_events(request):
    member_data = Member.objects.get(username=request.user.username)
    query = request.GET.get('query', '')

    # เฉพาะอีเว้นท์ที่ตรงกับคำค้นหาและไม่ถูกแบน
    events = Event.objects.filter(
        is_active=True,  
        created_by__is_banned=False,  
        created_by__is_active=True,  
    ).filter(
        Q(event_name__icontains=query) |  # ค้นหาจากชื่อกิจกรรม
        Q(event_title__icontains=query) |  # ค้นหาจากชื่อเรื่อง
        Q(location__icontains=query) |  # ค้นหาจากสถานที่
        Q(category__icontains=query) |  # ค้นหาจากหมวดหมู่
        Q(province__icontains=query) |  # ค้นหาจากจังหวัด
        Q(created_by__username__icontains=query)  # ค้นหาจากชื่อผู้สร้างโพสต์
    )

    context = {
        'member_data': member_data,
        'events': events, 
        'query': query,
    }
    return render(request, 'member/feed.html', context)
   

def filter_events(request):
    province_choices = EventForm.base_fields['province'].choices
    category_choices = EventForm.base_fields['category'].choices

    max_participants_range = range(1, 21)  

    events = Event.objects.all()
    
    province = request.GET.get('province', None)
    category = request.GET.get('category', None)
    max_participants = request.GET.get('max_participants', None)

    if province:
        events = events.filter(province=province)
    if category:
        events = events.filter(category=category)
    if max_participants:
        events = events.filter(max_participants__gte=max_participants)

    return render(request, 'member/feed.html', {
        'events': events,
        'province_choices': province_choices,
        'category_choices': category_choices,
        'max_participants_range': max_participants_range,
    })

# ส่งคำขอเข้าร่วมอีเว้น
def send_join_request(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=400)

    event = get_object_or_404(Event, id=event_id)
    sender = request.user
    receiver = get_object_or_404(Member, id=event.created_by_id)

    # ตรวจสอบว่าผู้ใช้เคยส่งคำขอแล้วหรือยัง
    if Event_Request.objects.filter(event=event, sender=sender).exists():
        return JsonResponse({'message': 'คุณเคยส่งคำขอเข้าร่วมกิจกรรมนี้แล้ว'}, status=400)

    # สร้าง Event_Request และเก็บไว้ในตัวแปร
    event_request = Event_Request.objects.create(
        event=event,
        sender=sender,
        receiver=receiver,
        response_status='pending'
    )

    # สร้างลิงก์ไปยังโปรไฟล์ของ sender
    sender_profile_url = request.build_absolute_uri(reverse('member_profile', args=[sender.id]))

    # สร้างข้อความที่มีลิงก์
    message = f"<a href='{sender_profile_url}'>{sender.username}</a> ต้องการเข้าร่วมกิจกรรม '{event.event_name}' ของคุณ"
    
    Notification.objects.create(
        user=receiver,
        message=message,
        related_event=event,
        related_request=event_request, 
        notification_type='request'
    )

    return JsonResponse({'message': 'ส่งคำขอสำเร็จ!'}, status=200)


# ตอบรับ/ปฏิเสธ คำขอ
def handle_event_request(request, event_request_id):
    try:
        if request.method == 'POST':
            action = request.POST.get('action')  
            event_request_instance = get_object_or_404(Event_Request, id=event_request_id)

            if action == 'accept':
                event_request_instance.response_status = 'accepted'
                event_request_instance.save()

                # สร้างห้องแชทพร้อมอีเว้น
                chat_room, created = ChatRoom.objects.get_or_create(event=event_request_instance.event)
                
                chat_room.members.add(event_request_instance.sender)

                chat_room_url = f"/chat/{chat_room.id}/"

                message = f"""
                    คำขอเข้าร่วมกิจกรรม '{event_request_instance.event.event_name}' ของคุณได้รับการอนุมัติแล้ว
                    <a href='{chat_room_url}' class='btn-join-chat'>แชทเลย!</a>
                """
                Notification.objects.create(
                    user=event_request_instance.sender,  
                    message=message,
                    related_event=event_request_instance.event,
                    related_request=event_request_instance, 
                    notification_type='response',
                )

                chat_room, created = ChatRoom.objects.get_or_create(event=event_request_instance.event)
                
                # แสดงว่าใครเขาร่วม
                Chat_Message.objects.create(
                    chatroom=chat_room,  
                    sender=None,  
                    message=f"{event_request_instance.sender.username} เข้าร่วมกิจกรรม '{event_request_instance.event.event_name}' เรียบร้อยแล้ว!",  # ใช้ message แทน content
                    created_at=now(),  
                    is_system_message=True,  
                )
                return JsonResponse({'message': 'คำขอได้รับการอนุมัติแล้ว!', 'chat_room_url': chat_room_url})

            elif action == 'reject':
                event_request_instance.response_status = 'rejected'
                event_request_instance.save()

                message = f"คำขอเข้าร่วมกิจกรรม '{event_request_instance.event.event_name}' ของคุณถูกปฏิเสธ"
                Notification.objects.create(
                    user=event_request_instance.sender, 
                    message=message,
                    related_event=event_request_instance.event,
                     related_request=event_request_instance, 
                    notification_type='response',
                )
                return JsonResponse({'message': 'คำขอถูกปฏิเสธแล้ว!'})

            else:
                return JsonResponse({'message': 'Invalid action'}, status=400)
        else:
            return JsonResponse({'message': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}'}, status=500)




@login_required
def event_review_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # ดึงสมาชิกจาก ChatRoom ของ Event
    chat_room = ChatRoom.objects.filter(event=event).first()
    if not chat_room:
        members = []
    else:
        members = chat_room.members.all()

    # ดึงข้อมูลรีวิวที่มีอยู่แล้ว
    reviewed_members = Event_Review.objects.filter(event=event, reviewer=request.user).values_list('participant_id', flat=True)

    return render(request, 'member/event/review_event_list.html', {
        'event': event,
        'members': members,
        'reviewed_members': reviewed_members
    })

def event_review_form(request, event_id, member_id):
    event = get_object_or_404(Event, id=event_id)
    participant = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        form = EventReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.reviewer = request.user
            review.participant = participant
            review.save()
            return redirect('review_event', event_id=event.id)  # กลับไปหน้ารายการสมาชิก
    else:
        form = EventReviewForm()

    return render(request, 'member/event/review_event_form.html', {
        'form': form,
        'event': event,
        'participant': participant
    })


# def review_event(request, event_id):
#     event = get_object_or_404(Event, id=event_id)

#     # ดึงผู้เข้าร่วมกิจกรรมจาก EventRequest โดยเช็คว่าเป็น "accepted"
#     participants = Member.objects.filter(id__in=Event_Request.objects.filter(event=event, response_status='accepted').values('receiver_id'))

#     if request.method == "POST":
#         for participant in participants:
#             status = request.POST.get(f"status_{participant.id}", "attended")
#             comment = request.POST.get(f"comment_{participant.id}", "")

#             EventReview.objects.create(
#                 event=event,
#                 reviewer=request.user,  # ผู้รีวิว
#                 participant=participant,  # ผู้ถูกรีวิว
#                 attendance_status=status,
#                 comment=comment
#             )
#         return redirect('previous_page')  # กลับไปยังหน้าก่อนหน้านี้

#     context = {"event": event, "participants": participants}
#     return render(request, "member/event/review_event.html", context)

# ปฏิทิน
@login_required
def user_events_api(request):
    user = request.user  # ดึง user ที่ล็อกอิน

    chat_rooms = ChatRoom.objects.filter(members=user)

    relevant_events = [chat_room.event for chat_room in chat_rooms if chat_room.event.is_active]

    category_colors = {
        'การศึกษา': '#3498db',
        'กีฬา': '#ff5733',
        'ท่องเที่ยว': '#f1c40f',
        'อาหาร': '#e67e22',
        'ศิลปะ': '#9b59b6',
        'สุขภาพ': '#2ecc71',
        'ความบันเทิง': '#e74c3c'
    }

    # แปลงกิจกรรมเป็น JSON
    data = [
        {
            'title': event.event_name,
            'start': event.event_datetime.isoformat(),
            'description': event.event_title,
            'location': event.location,
            'category': event.category,
            'province': event.province,
            'created_by': event.created_by.username,
            'max_participants': event.max_participants,
            'color': category_colors.get(event.category, '#95a5a6'),  # ใช้สีเริ่มต้นถ้าไม่พบหมวดหมู่
            'allDay': False
        }
        for event in relevant_events
    ]
    return JsonResponse(data, safe=False)

def notification_list(request):
    """ดึงแจ้งเตือนที่ถึงเวลาแล้วเท่านั้น"""
    notifications = Notification.objects.filter(
        user=request.user,
        is_scheduled=False  # ✅ แสดงแจ้งเตือนที่เปิดเผยแล้ว
    ).order_by('-created_at')

    return render(request, 'member/notifications.html', {'notifications': notifications})

def create_event_notifications(event):
    """สร้างแจ้งเตือนล่วงหน้า สำหรับเจ้าของ Event และผู้เข้าร่วม"""
    participants = list(Event_Request.objects.filter(
        event=event, response_status="accepted"
    ).values_list('sender', flat=True))

    recipients = [event.created_by.id] + participants  

    for user_id in recipients:
        message = f"กิจกรรม {event.event_name} ของคุณเป็นยังไงบ้าง? มารีวิวกันเถอะ!"

        review_link = reverse('review_event', kwargs={'event_id': event.id})  

        full_message = f"{message} <a href='{review_link}'>คลิกที่นี่</a>"

        print(f"🔔 กำลังสร้างแจ้งเตือนให้ User ID: {user_id}") 

        Notification.objects.create(
            user_id=user_id,
            message=full_message,
            related_event=event,
            notification_type="อื่น ๆ",
            is_scheduled=True,  
            scheduled_time=event.event_datetime,
            is_read=False
        )


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.related_event_id != request.user:
        return JsonResponse({'message': 'Unauthorized'}, status=403)

    notification.is_read = True
    notification.save()
    return JsonResponse({'message': 'Notification marked as read.'}, status=200)


def logout_view(request):
    logout(request) 
    return redirect('login')  

