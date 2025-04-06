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
# from django.utils.timesince import timesince
from django.contrib.admin.views.decorators import staff_member_required
# from django.views.decorators.csrf import csrf_exempt
# from django.db.models.functions import TruncMonth
from django.db.models import Count
# from django.db.models.signals import post_save, pre_delete
# from django.dispatch import receiver
from django.utils.timezone import now
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .serializers import ChatMessageSerializer
# from django.core.management.base import BaseCommand
from django.urls import reverse
from django.db.models.functions import TruncMonth
import json


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_banned:  
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



@staff_member_required
def admin_dashboard(request):
    members = Member.objects.filter(is_banned=False,is_superuser=False)
    total_members = members.count()

    users = Member.objects.all()
    total_users = users.count()
    total_delete_member = total_users - total_members

    reports = Report.objects.all()
    total_warned_event = reports.filter(is_warned='เตือน').count()

    total_events = Event.objects.count()
    total_events_active = Event.objects.filter(is_active=True).count()

    new_users_today = Member.objects.filter(date_joined__date=timezone.now().date()).count()
    events_created_today = Event.objects.filter(created_at__date=timezone.now().date()).count()

    total_reported_events = Event.objects.filter(is_active=False).count()

    # แปลงเดือนให้อยู่ในรูปแบบภาษาไทย
    month_labels = {
        '01': 'ม.ค.', '02': 'ก.พ.', '03': 'มี.ค.', '04': 'เม.ย.', '05': 'พ.ค.', 
        '06': 'มิ.ย.', '07': 'ก.ค.', '08': 'ส.ค.', '09': 'ก.ย.', '10': 'ต.ค.', 
        '11': 'พ.ย.', '12': 'ธ.ค.'
    }

    # ผู้ใช้ที่สมัครสมาชิกในแต่ละเดือน
    monthly_signups = (
        Member.objects.filter(is_banned=False, is_superuser=False)
        .annotate(month=TruncMonth('date_joined'))  
        .values('month')
        .annotate(count=Count('id'))  
        .order_by('month')
    )

    # กิจกรรมที่ถูกสร้างในแต่ละเดือน
    monthly_events = (
        Event.objects.filter(is_active=True)
        .annotate(month=TruncMonth('created_at'))  
        .values('month')
        .annotate(event_count=Count('id'))
        .order_by('month')
    )

    #list จำนวนสมาชิกที่สมัคร
    months = [month_labels[entry['month'].strftime('%m')] for entry in monthly_signups]
    members_count = [entry['count'] for entry in monthly_signups]

    #list จำนวนกิจกรรม
    event_months = [month_labels[entry['month'].strftime('%m')] for entry in monthly_events]
    event_counts = [entry['event_count'] for entry in monthly_events]


    context = {
        'total_members': total_members,
        'total_users': total_users,
        'total_delete_member':total_delete_member,
        'total_events': total_events,
        'total_events_active': total_events_active,
        'users': users,  
        'members': members,  
        'reports': reports,  
        'total_warned_event': total_warned_event,  
        'months': json.dumps(months),  # แปลงเป็น JSON เพื่อส่งไป JavaScript
        'members_count': json.dumps(members_count),
        'event_months': json.dumps(event_months), 
        'event_counts': json.dumps(event_counts),  
        'events_created_today': events_created_today,
        'new_users_today': new_users_today,
        'total_reported_events': total_reported_events,
        }
    return render(request, 'admin/dashboard.html',context)


@staff_member_required
def userdata_admin(request):
    members = Member.objects.filter(is_banned=False,is_superuser=False)
    members = members.annotate(activity_count=Count('events'))  
    total_members = members.count()  

    users = Member.objects.all()
    total_users = users.count()

    total_banned_member = total_users - total_members

    male_members = users.filter(sex='ชาย').count() 
    female_members = users.filter(sex='หญิง').count()

    male_members_active = members.filter(sex='ชาย').count() 
    female_members_active = members.filter(sex='หญิง').count()

    male_members_banned = users.filter(sex='ชาย', is_banned=True).count()
    female_members_banned = users.filter(sex='หญิง', is_banned=True).count()

    total_events = Event.objects.count()
    events_by_category = Event.objects.values('category').annotate(event_count=Count('id'))

    context = {
        'total_members': total_members,       
        'male_members': male_members,         
        'female_members': female_members,    
        'male_members_active': male_members_active,         
        'female_members_active': female_members_active,    
        'male_members_banned': male_members_banned,         
        'female_members_banned': female_members_banned, 
        'total_users': total_users,          
        'total_events': total_events,         
        'events_by_category': events_by_category,  
        'total_banned_member': total_banned_member, 
        'members': members,                   
        'users': users,                       
    }
    return render(request, 'admin/userdata_admin.html', context)

@staff_member_required
def block_user(request, id):
    if request.method == 'POST':
        try:
            member = get_object_or_404(Member, id=id) # ตรวจสอบว่ามีผู้ใช้ในระบบหรือไม่
            member.is_banned = True   
            member.is_active = False 
            member.save()
            return JsonResponse({'status': 'success', 'message': f'{member.username} ถูกแบนแล้ว'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@staff_member_required
def edit_member(request, member_id):
    # member_data = Member.objects.get(username=request.user.username) 
    member_data = get_object_or_404(Member, id=member_id)  

    if request.method == 'POST':
        # form = MemberUpdateForm(request.POST, request.FILES, instance=member)
        form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
        if form.is_valid():
            form.save()  
            return redirect('userdata')  
    else:
        form = MemberUpdateForm(instance=member_data)  

    context = {
        'form': form,
        'member_data': member_data,
    }
    return render(request, 'admin/edit_member.html', context)

@staff_member_required
def report_admin(request):
    reports = Report.objects.all()

    waiting_reports = reports.filter(is_warned='รอดำเนินการ')

    unique_reports = waiting_reports.values('event', 'report_type').distinct()

    total_reports = reports.count()
    total_waiting = unique_reports.count() 
    total_warned = reports.filter(is_warned='เตือน').count()
    total_rejected = reports.filter(is_warned='ปฏิเสธการรายงาน').count()

   
    system_issues = unique_reports.filter(report_type='ความผิดพลาดของระบบ').count()
    inappropriate_behavior = unique_reports.filter(report_type='พฤติกรรมไม่เหมาะสม').count()
    other_issues = unique_reports.filter(report_type='Other').count()

    context = {
        'total_reports': total_reports,        
        'total_waiting': total_waiting,     
        'total_warned': total_warned,          
        'total_rejected': total_rejected,       
        'system_issues': system_issues,        
        'inappropriate_behavior': inappropriate_behavior, 
        'other_issues': other_issues,           
        'waiting_reports': waiting_reports, 
    }

    return render(request, 'admin/report_admin.html', context)

@staff_member_required
def event_detail_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reports = Report.objects.filter(event=event)

    if request.method == "POST":
        action = request.POST.get("action")  

        if action == "warn":
            if reports.exists():# ตรวจสอบว่ามีรายงานหรือไม่
                reports.update(is_warned="เตือน")

                event.is_active = False
                event.save()

                Notification.objects.create(
                    user=event.created_by,  # ผู้สร้างอีเว้นท์
                    message=f"กิจกรรม '{event.event_name}' ของคุณถูกลบเนื่องจากละเมิดกฎชุมชน",  # ข้อความการแจ้งเตือน
                    notification_type="system",  # ประเภทของการแจ้งเตือน
                    related_event=event  # เชื่อมโยงกับอีเว้นท์ที่เกี่ยวข้อง
                )

        elif action == "reject":
            if reports.exists():
                reports.update(is_warned="ปฏิเสธการรายงาน")
            else:
                messages.error(request, "ไม่พบรายงานสำหรับกิจกรรมนี้")

        return redirect('report_admin')
    
    context = {
            'event': event,
            'reports': reports,
    }

    return render(request, 'admin/event_report_detail.html', context)

@login_required
def submit_report(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.event = event
            report.event_owner = event.created_by  
            report.description = form.cleaned_data['description']
            report.save()
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

    total_on_time_reviews = Event_Review.objects.filter(participant=member_data, attendance_status='มาตามนัด')
    total_not_on_time_reviews = Event_Review.objects.filter(participant=member_data, attendance_status='ผิดนัด')


    # ฟอร์มแก้ไขโปรไฟล์
    if request.method == 'POST':
        if 'update_profile' in request.POST:  # ตรวจสอบว่ามาจากการอัปเดตโปรไฟล์
            form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
            if form.is_valid():
                form.save()  
                return redirect('profile')  

        elif 'event_submit' in request.POST:  
            event_id = request.POST.get('event_id')
            if event_id:  
                event = get_object_or_404(Event, id=event_id, created_by=request.user)
                event_form = EventForm(request.POST, instance=event)


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
        'total_on_time_reviews': total_on_time_reviews,
        'total_not_on_time_reviews': total_not_on_time_reviews,  
        # 'active_events': active_events,  
        # 'active_events_count': active_events_count,
        'form': form,
        'event_form': event_form,  # ฟอร์มสร้าง/แก้ไขกิจกรรม
        "provinces": PROVINCES
    }
    return render(request, 'member/profile.html', context)


@login_required
def member_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    user_login = Member.objects.get(username=request.user.username)

    events = Event.objects.filter(created_by=member, is_active=True)
    total_events = events.count()

    total_joined_events = Event_Request.objects.filter(sender=member, response_status='accepted').count()
    
    total_on_time_reviews = Event_Review.objects.filter(participant=member, attendance_status='มาตามนัด').count()
    total_not_on_time_reviews = Event_Review.objects.filter(participant=member, attendance_status='ผิดนัด').count()

    context = {
        'user_login':user_login,
        'member': member,
        'events':events,
        'total_events':total_events,
        'total_joined_events': total_joined_events,
        'total_on_time_reviews': total_on_time_reviews,
        'total_not_on_time_reviews': total_not_on_time_reviews,  
        
    } 
    return render(request, 'member/member_profile.html', context)

# เช็คในลงทะเบียน
def check_username_register(request):
    username = request.GET.get("username", None)
    exists = Member.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})

# เช็คในฟอร์ม
@login_required
def check_username(request):
    username = request.GET.get("username", None)
    
    if username == request.user.username:
        return JsonResponse({"exists": False})  

    exists = Member.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})


@login_required    
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

    context = {
        'chat_room': chat_room,
        'messages': messages,
        'member_data': member_data,
    }

    return render(request, 'member/chat/chat_room_detail.html',context)

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


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()  
        return redirect('profile')  

# สร้างอีเว้น
@login_required
def new_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

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
    return render(request, 'member/feed.html', {'form': form})


 
# ค้นหาอีเว้น
@login_required
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

    sender_profile_url = request.build_absolute_uri(reverse('member_profile', args=[sender.id]))
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
@login_required
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

                
                # แสดงว่าใครเขาร่วม
                Chat_Message.objects.create(
                    chatroom=chat_room,  
                    sender=None,  
                    message=f"{event_request_instance.sender.username} เข้าร่วมกิจกรรม '{event_request_instance.event.event_name}' เรียบร้อยแล้ว!",  # ใช้ message แทน content
                    created_at=now(),  
                    is_system_message=True,  
                )
                return JsonResponse({'message': 'คำขอได้รับการอนุมัติแล้ว!'})

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

    context = {
        'event': event,
        'members': members,
        'reviewed_members': reviewed_members
    }
    return render(request, 'member/review/review_event_list.html',context)

@login_required
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

    context = {
        'form': form,
        'event': event,
        'participant': participant
    }
    return render(request, 'member/review/review_event_form.html', context)



# ปฏิทิน
def user_events_api(request):
    user = request.user  

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

@login_required
def logout_view(request):
    logout(request) 
    return redirect('login')  