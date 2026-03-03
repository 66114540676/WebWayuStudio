from django.urls import path
from . import views

urlpatterns = [

    path('create_order/', views.create_order_framings, name='create_order_framings'), # URL สำหรับสร้างออเดอร์สั่งทำกรอบรูป
    path('order/<int:order_id>/confirm/', views.checkout_order_framings, name='checkout_order_framings'), # URL สำหรับยืนยันออเดอร์กรอบรูป
    path('order/success/', views.order_framings_success, name='order_framings_success'), # URL สำหรับหน้าสำเร็จหลังจากสั่งทำกรอบรูป

    path('manager/dashboard/', views.ShopManagerView.as_view(), name='order_framings_manager'), # URL สำหรับหน้าจัดสินค้ากรอบรูป
    path('manager/order/<int:order_id>/update/', views.update_order_status, name='update_framing_status'), # URL สำหรับอัพเดทสถานะออเดอร์กรอบรูป
    path('manager/order/<int:order_id>/delete/', views.delete_order, name='delete_framing_order'), # URL สำหรับลบออเดอร์กรอบรูป

    path('framings/admin/manager/edit/<int:order_id>/', views.edit_order_framings, name='edit_order_framings'), # URL สำหรับแก้ไขออเดอร์กรอบรูปโดยแอดมิน
]