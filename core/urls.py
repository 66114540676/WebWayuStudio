from django.urls import path
from . import views
from .views import HomePageView, DashboardView, UserManageView, toggle_user_status, delete_user

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'), # หน้า Dashboard (Admin)

    path('dashboard/users/', UserManageView.as_view(), name='admin_user_manage'), # หน้า User Management (Admin)
    path('dashboard/users/toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'), # Toggle User Status (Admin)
    path('dashboard/users/delete/<int:user_id>/', delete_user, name='delete_user'), # Delete User (Admin)
    path('toggle-staff/<int:user_id>/', views.toggle_staff_status, name='toggle_staff_status'), # Toggle Staff Status (Admin)


    path('dashboard/calendar/', views.admin_calendar, name='admin_calendar'), # หน้า ปฏิทินกิจกรรม (Admin)
    path('dashboard/calendar/edit/<int:event_id>/', views.edit_event, name='edit_event'), # แก้ไขกิจกรรม (Admin)
    path('dashboard/calendar/delete/<int:event_id>/', views.delete_event, name='delete_event'), # ลบกิจกรรม (Admin)
    path('api/calendar-events/', views.calendar_events, name='calendar_events'), # API สำหรับดึงข้อมูลกิจกรรม (Admin)
]