from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), # C (Create) - เพิ่มสินค้าลงในตะกร้า
    path('', views.cart_detail, name='cart_detail'),  # R (Read) - ดูรายละเอียดตะกร้า
    path('update/<int:item_id>/', views.update_cart, name='update_cart'), # U (Update) - แก้ไขจำนวนสินค้าในตะกร้า
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), # D (Delete) - ลบรายการสินค้าออกจากตะกร้า
]