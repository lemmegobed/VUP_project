from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
# from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", login_view,name='login'),
    path('custom-admin/dashboard/', admin_dashboard, name='dashboard'),
    path('custom-admin/userdata/', userdata_admin, name='userdata'),
    path('custom-admin/report/', report_admin, name='report_admin'),
    # path('delete-member/<int:id>/', delete_member, name='delete_member'),
    path('block/<int:id>/', block_user, name='block_user'),
    path('edit-member/<int:member_id>/', edit_member, name='edit_member'),
    path('upload-ads/', upload_ads, name='upload_ads'),

    # path('warn_member/<int:id>/', warn_member, name='warn_member'),
    path('warn_event/<int:event_id>/', warn_event, name='warn_event'),
    # path('event/report/<int:event_id>/', event_detail_report, name='event_report_detail'),
    path('event/report/<int:event_id>/', event_detail_report, name='event_detail_report'),

    path("register/", register_view,name='register'),
    path("feed/", home_view,name='feed'),
    # path('report/', submit_report, name='submit_report'),
    path('report/<int:event_id>/', submit_report, name='submit_report'),

    path('profile/', profile_view, name='profile'),
    path('profile/<int:member_id>/edit', profile_edit, name='edit_profile'),
    path('my-activity/', my_activity, name='my_activity'),
    path('chat/', chat_rooms_list, name='chat'),
    # path('chatroom/<int:event_id>/', chat_room_detail, name='chat_room'),
    # path('chatroom/<int:chat_room_id>/', views.chat_room, name='chat_room'),
    # path('chat-room/<int:chat_room_id>/', views.chat_room, name='chat_room'),
    path('chat-room/<int:chat_room_id>/', chat_room_detail, name='chat_room'),

    path("event/<int:event_id>/review/", review_event, name="review_event"),

    # path('api/check-participant-status/<int:event_id>/', check_participant_status, name='check_participant_status'),

    # path('api/events/', events_api, name='events_api'),
    path('api/user-events/', user_events_api, name='user_events_api'),

    path('new_event/', new_event_view, name='new_event'),
    # path('update_event/<int:event_id>/', update_event_view, name='update_event'),
    # path('edit-event/<int:event_id>/', edit_event, name='edit_event'),
    # path("event/<int:event_id>/join/",request_to_join, name="request_to_join"),
    # path("notification/<int:notification_id>/<str:action>/", respond_to_request, name="respond_to_request"),
    path('notifications/<int:notification_id>/mark-as-read/',mark_notification_as_read, name='mark_notification_as_read'),
    
    path('events/<int:event_id>/send-request/', send_join_request, name='send_join_request'),
    # path('requests/<int:request_id>/handle/', action_request, name='action_request'),
    # path('requests/<int:request_id>/handle/', handle_request_action, name='handle_request_action'),
    # path('requests/<int:request_id>/handle/', handle_request_action, name='handle_request_action'),
    # path('events/<int:event_id>/handle-request/', handle_event_request, name='handle_event_request'),
    # path('events/<int:event_id>/handle-request/', handle_event_request, name='handle_event_request'),
    path('events/requests/<int:event_request_id>/handle-request/', handle_event_request, name='handle_event_request'),
    # path('notifications/', notifications_view, name='notifications'),  
    
    # path("chatroom/<int:event_id>/", chat_list, name="chatroom"),
    # path('chat/', chat_list, name='chat_list'),
    
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),
    path('search/', search_events, name='search_events'),
    path('filter/', filter_events, name='filter_events'),
    
    path('logout/', logout_view, name='logout'),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

   
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)