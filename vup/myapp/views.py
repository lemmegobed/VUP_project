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

@receiver(pre_delete, sender=Member)
def handle_member_deletion(sender, instance, **kwargs):
    # ตั้งค่า Member ใน User ให้เป็น NULL ก่อนลบ Member
    User.objects.filter(member=instance).update(member=None)

# @staff_member_required
def admin_dashboard(request):

    members = Member.objects.all()
    total_members = Member.objects.count()

    users = User.objects.all()
    total_users = User.objects.count()

    total_delete_member = total_users - total_members

    male_members = Member.objects.filter(sex='M').count() 
    female_members = Member.objects.filter(sex='F').count()  

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
        }
    return render(request, 'admin/dashboard.html',context)

def userdata_admin(request):
    members = Member.objects.filter(is_banned=False)
    members = members.annotate(activity_count=Count('events'))  
    total_members = members.count()  

    users = User.objects.all()
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

# def warn_member(request, member_id):
#     # ดึงข้อมูลของ Member ที่เป็นเจ้าของอีเว้น
#     member = get_object_or_404(Member, id=member_id)

#     # สร้างการแจ้งเตือน
#     Notification.objects.create(
#         user=member,  # ส่งการแจ้งเตือนไปยัง member
#         message=f"You have been warned for an issue with your event.",
#     )
#     messages.success(request, f"Warning has been sent to {member.username}.")

#     return redirect('report_admin') 

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
    # ดึงข้อมูลรายงานทั้งหมด
    reports = Report.objects.all()

    # กรองเฉพาะรายงานที่ยังรอดำเนินการ
    waiting_reports = reports.filter(is_warned='รอดำเนินการ')

    # จัดกลุ่มการเตือน: 1 อีเวนต์ + 1 เรื่อง
    unique_reports = waiting_reports.values('event', 'report_type').distinct()

    # นับจำนวนสถานะ
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
    # ดึงข้อมูลอีเวนต์ตาม event_id
    event = get_object_or_404(Event, id=event_id)
    
    # ดึงรายงานทั้งหมดสำหรับอีเวนต์นี้
    reports = Report.objects.filter(event=event)

    if request.method == "POST":
        action = request.POST.get("action")  # รับค่าปุ่มที่กด
        report_type = request.POST.get("report_type")  # รับประเภทของรายงานที่เลือก
        
        if action == "warn":
            # ตรวจสอบว่ามีการเตือนสำหรับ event + report_type แล้วหรือยัง
            warned_reports = reports.filter(report_type=report_type, is_warned='เตือน')
            if warned_reports.exists():
                messages.warning(request, f"The event '{event.event_name}' has already been warned for '{report_type}'.")
            else:
                # อัปเดตสถานะเป็นเตือนสำหรับ report_type นี้
                reports.filter(report_type=report_type).update(is_warned='เตือน')
                # บันทึกข้อมูล
                Report.objects.create(
                    event=event,
                    report_type=report_type,
                    is_warned='เตือน',
                    reporter=request.user 
                )
                messages.success(request, f"The event '{event.event_name}' has been marked as warned for '{report_type}'.")

        elif action == "reject":
            # อัปเดตสถานะเป็นปฏิเสธสำหรับ report_type นี้
            rejected_reports = reports.filter(report_type=report_type, is_warned='ปฏิเสธการรายงาน')
            if rejected_reports.exists():
                messages.warning(request, f"The report for the event '{event.event_name}' has already been rejected for '{report_type}'.")
            else:
                reports.filter(report_type=report_type).update(is_warned='ปฏิเสธการรายงาน')
                # บันทึกข้อมูล
                Report.objects.create(
                    event=event,
                    report_type=report_type,
                    is_warned='ปฏิเสธการรายงาน',
                    reporter=request.user  # เพิ่มผู้รายงาน
                )
                messages.success(request, f"The report for the event '{event.event_name}' has been rejected for '{report_type}'.")

        return redirect('report_admin')  # กลับไปยังหน้า report_admin

    # ส่งข้อมูลไปยัง template
    return render(request, 'admin/event_report_detail.html', {
        'event': event,
        'reports': reports,
    })



# def event_detail_report(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     report = get_object_or_404(Report, event=event)
#     if request.method == "POST":
#         action = request.POST.get("action")  # รับค่าปุ่มที่กด
#         if action == "warn":  # กดปุ่มรายงาน
#             report.is_warned = 'เตือน'
#             report.save()
#             messages.success(request, f"The event '{event.event_name}' has been marked as reported.")
#         elif action == "reject":  # กดปุ่มปฏิเสธ
#             report.is_warned = 'ปฏิเสธการรายงาน'
#             report.save()
#             messages.success(request, f"The report for the event '{event.event_name}' has been rejected.")
#         return redirect('report_admin')  # กลับไปยังหน้า report_admin

#     return render(request, 'admin/event_report_detail.html', {'event': event, 'report': report})

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


# def submit_report(request, event_id):
#     event = get_object_or_404(Event, id=event_id) 
#     if request.method == 'POST':
#         form = ReportForm(request.POST)
#         if form.is_valid():
#             report = form.save(commit=False)
#             report.reporter = request.user  
#             report.event = event  
#             report.event_owner = event.created_by  
#             report.save()
#             return redirect('feed')  
#     else:
#         form = ReportForm()

#     context = {
#         'form': form,
#         'event': event,
#     }
#     return render(request, 'member/submit_report.html', context)

@login_required
def home_view(request):
    # กรองกิจกรรมเฉพาะที่สร้างโดยผู้ใช้ที่ไม่ถูกแบนและยัง active
    events = Event.objects.filter(
        created_by__is_banned=False,
        created_by__is_active=True
    )  # เพิ่ม select_related เพื่อปรับปรุงประสิทธิภาพ

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

def chat_view(request):
    member_data = Member.objects.get(username=request.user.username)
    return render(request, 'member/chat.html', {'member_data': member_data})

def my_activity(request):
    user_events = Event.objects.filter(created_by=request.user)
    member_data = Member.objects.get(username=request.user.username) 
    form = EventForm()  
    total_events = user_events.count()

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
        'user_events': user_events,
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
        'events': events  # ส่งข้อมูลกิจกรรมไปที่เทมเพลต
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

def chat_view(request):
    member_data = Member.objects.get(username=request.user.username)
    return render(request, 'member/chat.html', {'member_data': member_data})

@login_required
def new_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)  
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  
            event.save() 

            return JsonResponse({'success': True})  
        else:
            return JsonResponse({'success': False, 'errors': form.errors})  

    else:
        form = EventForm() 
    return render(request, 'member/home.html', {'form': form})

# def event_list(request):
#     events = Event.objects.all()
#     for event in events:
#         event.time_since_created = timesince(event.created_at)  
#     return render(request, 'your_template.html', {'events': events})

# @csrf_exempt
# def request_to_join(request, event_id):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         receiver_id = data.get("receiver_id")
#         sender = request.user
#         event = Event.objects.get(id=event_id)

#         # บันทึก Notification
#         Notification.objects.create(
#             sender=sender,
#             receiver_id=receiver_id,
#             event=event,
#             message=f"{sender.username} ต้องการเข้าร่วมกิจกรรม {event.name}"
#         )

#         return JsonResponse({"message": "คำขอเข้าร่วมถูกส่งเรียบร้อยแล้ว"})
#     return JsonResponse({"error": "Invalid request"}, status=400)

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)


    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()  # บันทึกการเปลี่ยนแปลง
            return redirect('feed', event_id=event.id)  # ไปที่หน้ารายละเอียด event
    else:
        form = EventForm(instance=event)  # แสดงฟอร์มที่มีข้อมูลจาก event เดิม

    return render(request, 'member/feed.html', {'form': form, 'events': events})

# ฟังก์ชันสำหรับลบ Event
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()  
        return redirect('my_activity')  
    
# def delete_event(request, event_id): 
#     if request.method == "POST":
#         event = get_object_or_404(Event, id=event_id, created_by=request.user)
#         event.delete()
#         return redirect('my_activity')  
#     else:
#         return redirect('my_activity')  

def search_events(request):
    member_data = Member.objects.get(username=request.user.username) 
    query = request.GET.get('query', '')
    
    events = Event.objects.filter(
        Q(event_name__icontains=query) |
        Q(event_title__icontains=query) |
        Q(location__icontains=query)
    )
    context = {
        'member_data': member_data,
        'events': events, 
        'query': query,
    }

    return render(request, 'member/feed.html', context)
    # return render(request, 'member/home.html', {'events': events, 'query': query,'member_data': member_data})

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

def notifications_view(request):
    user = request.user  # ผู้ใช้ปัจจุบัน
    notifications = user.notifications.all()  # ดึงการแจ้งเตือนทั้งหมดของผู้ใช้
    return render(request, 'notifications.html', {'notifications': notifications})

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('receiver', 'sender', 'message', 'notification_type', 'is_read', 'created_at')
#     list_filter = ('notification_type', 'is_read', 'created_at')
#     search_fields = ('message', 'receiver__username', 'sender__username')

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



def action_request(request, request_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=400)

    data = json.loads(request.body)
    action = data.get('action')  # รับ action: 'accept' หรือ 'reject'

    # ดึงคำขอ
    event_request = get_object_or_404(Event_Request, id=request_id)

    if action == 'accept':
        event_request.response_status = 'accepted'
        message = f"คำขอกิจกรรม '{event_request.event.event_name}' ได้รับการอนุมัติแล้ว"
    elif action == 'reject':
        event_request.response_status = 'rejected'
        message = f"คำขอกิจกรรม '{event_request.event.event_name}' ถูกปฏิเสธ"
    else:
        return JsonResponse({'message': 'Invalid action'}, status=400)

    # บันทึกสถานะ
    event_request.save()

    # สร้างการแจ้งเตือนตอบกลับไปยังผู้ส่งคำขอ
    Notification.objects.create(
        receiver=event_request.sender,
        sender=request.user,
        message=message,
        related_event=event_request.event,
        notification_type='response'
    )

    return JsonResponse({'message': f'Request has been {action}ed successfully.'}, status=200)

    # return JsonResponse({'message': 'Request sent successfully!'}, status=200)

# def send_join_request(request, event_id):
#     if request.method != 'POST':
#         return JsonResponse({'message': 'รูปแบบคำขอไม่ถูกต้อง'}, status=400)

#     # ดึงข้อมูลกิจกรรมและผู้ใช้
#     event = get_object_or_404(Event, id=event_id)
#     sender = request.user  # ผู้ส่งคำขอ
#     receiver = get_object_or_404(Member, id=event.created_by_id)

#     # บันทึกคำขอเข้าร่วม
#     Event_Request.objects.create(
#         event=event,
#         sender=sender,
#         receiver=receiver,
#         response_status='pending'
#     )

#     # สร้างการแจ้งเตือน
#     message = f"{sender.username} ได้ส่งคำขอเข้าร่วมกิจกรรม {event.name} ของคุณ"
#     Notification.objects.create(
#         user=receiver,
#         message=message,
#         related_event=event,
#         notification_type='request'
#     )

#     return JsonResponse({'message': 'ส่งคำขอสำเร็จ!'}, status=200)


def respond_to_request(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'message': 'ส่งคำขอไม่สำเร็จ กรุณาลองใหม่อีกครั้ง'}, status=400)

    data = json.loads(request.body)
    action = data.get('action')

    event = get_object_or_404(Event, id=event_id)
    sender = request.user  # เจ้าของกิจกรรม
    event_request = get_object_or_404(Event_Request, event=event, receiver=sender)

    # อัปเดตสถานะคำขอ
    if action == 'accept':
        event_request.response_status = 'accepted'
        message = f"คำขอเข้าร่วมกิจกรรม {event.name} ของคุณได้รับการอนุมัติแล้ว"
    elif action == 'reject':
        event_request.response_status = 'rejected'
        message = f"คำขอเข้าร่วมกิจกรรม {event.name} ของคุณถูกปฏิเสธ"
    else:
        return JsonResponse({'message': 'คำสั่งไม่ถูกต้อง'}, status=400)

    event_request.save()

    # สร้างการแจ้งเตือน
    Notification.objects.create(
        user=event_request.sender,
        message=message,
        related_event=event,
        notification_type='response'
    )

    return JsonResponse({'message': f'คำขอถูก {action} แล้ว!'}, status=200)

# @login_required
# def request_to_join(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     owner = event.owner
#     sender = request.user

#     # สร้าง Notification
#     message = f"{sender.username} ต้องการเข้าร่วมกิจกรรม {event.name} ของคุณ"
#     Notification.objects.create(sender=sender, receiver=owner, event=event, message=message)

#     return JsonResponse({"message": "Request sent successfully"})


@login_required
# def respond_to_request(request, notification_id, action):
#     notification = get_object_or_404(Notification, id=notification_id)

#     if action == "approve":
#         notification.is_approved = True
#         notification.save()

#         # สร้าง ChatRoom หากยังไม่มี
#         chatroom, created = ChatRoom.objects.get_or_create(event=notification.event)
#         chatroom.users.add(notification.receiver, notification.sender)

#         # แจ้งผู้ขอว่าได้รับการอนุมัติ
#         approval_message = f"{notification.receiver.username} ได้ตอบรับคำขอเข้าร่วมกิจกรรม {notification.event.name} ของคุณ"
#         Message.objects.create(chatroom=chatroom, sender=notification.receiver, content=approval_message)

#         return JsonResponse({"message": "Request approved and chat room created"})

#     elif action == "reject":
#         notification.is_approved = False
#         notification.save()

#         # แจ้งผู้ขอว่าถูกปฏิเสธ
#         rejection_message = f"{notification.receiver.username} ได้ปฏิเสธคำขอเข้าร่วมกิจกรรม {notification.event.name} ของคุณ"
#         Message.objects.create(chatroom=None, sender=notification.receiver, content=rejection_message)

#         return JsonResponse({"message": "Request rejected"})

#     return JsonResponse({"error": "Invalid action"})

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.related_event_id != request.user:
        return JsonResponse({'message': 'Unauthorized'}, status=403)

    notification.is_read = True
    notification.save()
    return JsonResponse({'message': 'Notification marked as read.'}, status=200)

# @login_required
def chatroom_view(request, event_id):
    chatroom = get_object_or_404(ChatRoom, event__id=event_id)

    if request.method == "POST":
        content = request.POST.get("content")
        Message.objects.create(chatroom=chatroom, sender=request.user, content=content)

    messages = chatroom.messages.all()
    return render(request, "chatroom.html", {"chatroom": chatroom, "messages": messages})


def logout_view(request):
    logout(request) 
    return redirect('login')  

