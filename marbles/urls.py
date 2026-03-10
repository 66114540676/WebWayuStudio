from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.create_order_marbles, name='create_order_marbles'), # URL สำหรับฟอร์มสั่งทำป้าย
    path('checkout/<int:order_id>/', views.checkout_order_marbles, name='checkout_order_marbles'), # URL สำหรับหน้าชำระเงินคำสั่งทำป้าย
    path('order/success/', views.order_marbles_success, name='order_marbles_success'), # URL สำหรับหน้าขอบคุณหลังสั่งทำป้าย

    path('manager/', views.order_marbles_manager, name='order_marbles_manager'), # URL สำหรับหน้าจัดการคำสั่งทำป้าย
    path('manager/update/<int:order_id>/', views.update_order_status, name='update_order_status'), # URL สำหรับอัปเดตสถานะคำสั่งทำป้าย
    path('manager/delete/<int:order_id>/', views.delete_marbles_order, name='delete_marbles_order'), # URL สำหรับลบคำสั่งทำป้าย

    path('marbles/manager/edit/<int:order_id>/', views.edit_order_marbles, name='edit_order_marbles'), # URL สำหรับแก้ไขคำสั่งทำป้าย
]