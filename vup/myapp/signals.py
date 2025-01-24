# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import *

# @receiver(post_save, sender=Member)
# def deactivate_user_events(sender, instance, **kwargs):
#     if not instance.is_active:  # หากผู้ใช้ถูกปิดการใช้งาน
#         Event.objects.filter(created_by=instance).update(is_active=False)  # ซ่อนกิจกรรม
#     else:  # หากผู้ใช้ถูกเปิดใช้งานอีกครั้ง
#         Event.objects.filter(created_by=instance).update(is_active=True)  # คืนสถานะกิจกรรม
