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
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now, timedelta


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

# @receiver(pre_delete, sender=Member)
# def handle_member_deletion(sender, instance, **kwargs):
#     # ตั้งค่า Member ใน User ให้เป็น NULL ก่อนลบ Member
#     User.objects.filter(member=instance).update(member=None)

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
    return render(request, 'member/submit_report.html', context)



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



@login_required
def profile_view(request):
    member_data = Member.objects.get(username=request.user.username) 
    user_events = Event.objects.filter(created_by=request.user)  # ดึง Event ที่ผู้ใช้นี้สร้าง
    total_events = user_events.count()
    
    if request.method == 'POST':
        form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
        if form.is_valid():
            form.save()  
            return redirect('profile')  
    else:
        form = MemberUpdateForm(instance=member_data)  # กรณีไม่ใช่ POST ให้สร้างฟอร์มจากข้อมูลผู้ใช้ที่ล็อกอิน
    
    context = {
        'user_events': user_events,
        'total_events': total_events,  
        'form': form,
        'member_data': member_data
    }
    return render(request, 'member/profile.html', context)

# def chat_view(request):
#     member_data = Member.objects.get(username=request.user.username)
#     return render(request, 'member/chat.html', {'member_data': member_data})

def chat_rooms_list(request):
    
    member_data = Member.objects.get(username=request.user.username)
    user = request.user

    chat_rooms = ChatRoom.objects.filter(
        Q(created_by=user) | Q(members=user),  # ผู้ใช้เป็นเจ้าของ หรือเป็นสมาชิกในห้อง              # อีเว้นต์ไม่ได้ถูกแบน
        event__is_active=True                  # อีเว้นต์ต้อง active
    ).distinct()

    context = {
        'member_data': member_data,
        'chat_rooms': chat_rooms,
    }

    return render(request, 'member/chat.html', context)

def chat_room_detail(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    return render(request, 'member/chat_room_detail.html', {'chat_room': chat_room})

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

def profile_edit(request):
    member_data = Member.objects.get(username=request.user.username) 
    events = Event.objects.all()
    form = EventForm()
    user = request.user
    user_events = Event.objects.filter(created_by=request.user)

    
    if request.method == 'POST':
        form = MemberUpdateForm(request.POST, request.FILES, instance=member_data)
        if form.is_valid():
            form.save()  
            return redirect('profile')  
    else:
        form = MemberUpdateForm(instance=member_data)  # กรณีไม่ใช่ POST ให้สร้างฟอร์มจากข้อมูลผู้ใช้ที่ล็อกอิน
    
    context = {
        'user': user,
        'events': events, 
        'member_data': member_data,
        'events': events,
        'form': form,
        'events': user_events
    }
    return render(request, 'member/profile_edit.html', context)

# def chat_view(request):
#     member_data = Member.objects.get(username=request.user.username)
#     return render(request, 'member/chat.html', {'member_data': member_data})

# def chat_list(request):
#     # ดึงห้องแชทที่เกี่ยวข้องกับผู้ใช้ (เป็นเจ้าของหรือเป็นสมาชิก)
#     chat_rooms = ChatRoom.objects.filter(
#         models.Q(created_by=request.user) | models.Q(members=request.user)
#     ).distinct()

#     return render(request, 'chat.html', {'chat_rooms': chat_rooms})

# สร้างอีเว้น
@login_required
def new_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

            # สร้าง ChatRoom
            chat_room = ChatRoom.objects.create(
                name=event.event_name,
                event=event,
                created_by=request.user  # ใช้ request.user ที่รองรับ AUTH_USER_MODEL
            )
            chat_room.members.add(request.user)  # เพิ่มผู้สร้างเป็นสมาชิกคนแรก

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
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()  
        return redirect('my_activity')  
 
# ค้นหาอีเว้น
def search_events(request):
    member_data = Member.objects.get(username=request.user.username) 
    query = request.GET.get('query', '')
    
# กรองเฉพาะอีเว้นท์ที่ตรงกับคำค้นหาและไม่ถูกแบน
    events = Event.objects.filter(
        is_active=True,  # เฉพาะอีเว้นท์ที่ยัง active
        created_by__is_banned=False,  # ผู้สร้างอีเว้นท์ไม่ถูกแบน
        created_by__is_active=True,  # ผู้สร้างอีเว้นท์ยัง active
    ).filter(
        Q(event_name__icontains=query) |  # ค้นหาชื่ออีเว้นท์
        Q(event_title__icontains=query) |  # ค้นหาชื่อเรื่องของอีเว้นท์
        Q(location__icontains=query)  # ค้นหาสถานที่ของอีเว้นท์
    )

    context = {
        'member_data': member_data,
        'events': events, 
        'query': query,
    }
    return render(request, 'member/feed.html', context)
   

# def filter_events(request):
#     member_data = Member.objects.get(username=request.user.username) 
#     category = request.GET.get('category', None)
#     max_participants = request.GET.get('max_participants', None)
#     province = request.GET.get('province', None)

#     events = Event.objects.all()  

#     if category:
#         events = events.filter(category=category)
#     if max_participants:
#         events = events.filter(max_participants__gte=max_participants) 
#     if province:
#         events = events.filter(province=province)

#     return render(request, 'member/home.html', {'events': events,'member_data': member_data})

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

    if Event_Request.objects.filter(event=event, sender=sender).exists():
        return JsonResponse({'message': 'คุณเคยส่งคำขอเข้าร่วมกิจกรรมนี้แล้ว'}, status=400)

    Event_Request.objects.create(
        event=event,
        sender=sender,
        receiver=receiver,
        response_status='pending'
    )

    message = f"{sender.username} ต้องการเข้าร่วมกิจกรรม '{event.event_name}' ของคุณ"
    Notification.objects.create(
        user=receiver,
        message=message,
        related_event=event,
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

                # สร้างการแจ้งเตือน
                message = f"กิจกรรม '{event_request_instance.event.event_name}' ของคุณได้รับการอนุมัติ!"
                Notification.objects.create(
                    user=event_request_instance.sender,  # แจ้งเตือนไปยัง sender
                    message=message,
                    related_event=event_request_instance.event,
                    notification_type='response',
                )
                return JsonResponse({'message': 'คำขอได้รับการอนุมัติแล้ว!'})

            elif action == 'reject':
                event_request_instance.response_status = 'rejected'
                event_request_instance.save()

                # สร้างการแจ้งเตือน
                message = f"คำขอเข้าร่วมกิจกรรม '{event_request_instance.event.event_name}' ของคุณถูกปฏิเสธ"
                Notification.objects.create(
                    user=event_request_instance.sender,  # แจ้งเตือนไปยัง sender
                    message=message,
                    related_event=event_request_instance.event,
                    notification_type='response',
                )
                return JsonResponse({'message': 'คำขอถูกปฏิเสธแล้ว!'})

            else:
                return JsonResponse({'message': 'Invalid action'}, status=400)
        else:
            return JsonResponse({'message': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}'}, status=500)


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.related_event_id != request.user:
        return JsonResponse({'message': 'Unauthorized'}, status=403)

    notification.is_read = True
    notification.save()
    return JsonResponse({'message': 'Notification marked as read.'}, status=200)

# @login_required
# def chatroom_view(request, event_id):
#     chatroom = get_object_or_404(ChatRoom, event__id=event_id)

#     if request.method == "POST":
#         content = request.POST.get("content")
#         Message.objects.create(chatroom=chatroom, sender=request.user, content=content)

#     messages = chatroom.messages.all()
#     return render(request, "chatroom.html", {"chatroom": chatroom, "messages": messages})


def logout_view(request):
    logout(request) 
    return redirect('login')  

