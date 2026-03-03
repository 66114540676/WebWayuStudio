from django.urls import path
from . import views
from .views import ProductDetailView

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'), # หน้าแสดงสินค้า
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'), # หน้าแสดงรายละเอียดสินค้า
    path('product/<int:pk>/checkout/', views.ProductCheckoutView.as_view(), name='product_checkout'), # หน้าสั่งซื้อสินค้า
    path('cart/checkout/', views.cart_stores_checkout, name='cart_stores_checkout'), # หน้าชำระเงินสินค้าทั้งหมดในตะกร้า
    path('order-success/', views.order_stores_success, name='order_stores_success'), # หน้า สั่งซื้อสำเร็จ (หลังจากชำระเงิน)
    
    path('products/', views.ProductManageListView.as_view(), name='product-manage-list'), # หน้า "รายการสินค้า" (Admin)
    path('products/add/', views.ProductCreateView.as_view(), name='product-add'), # หน้า เพิ่มสินค้า (Admin)
    path('products/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product-edit'), # หน้า แก้ไขสินค้า (Admin)
    path('products/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product-delete'), # หน้า ลบสินค้า (Admin)
    
    path('categories/', views.CategoryManageListView.as_view(), name='category-manage-list'), # หน้า "รายการหมวดหมู่" (Admin)
    path('category/add/', views.CategoryCreateView.as_view(), name='category-add'), # หน้า เพิ่มหมวดหมู่ (Admin)
    path('category/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category-edit'), # หน้า แก้ไขหมวดหมู่ (Admin)
    path('category/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category-delete'), # หน้า ลบหมวดหมู่ (Admin)

    path('admin/orders/', views.OrderManageListView.as_view(), name='admin-order-list'), # หน้า "รายการสั่งซื้อ" (Admin)
    path('admin/orders/<int:pk>/status/', views.admin_update_order_status, name='admin-order-update-status'), # หน้า อัพเดทสถานะการสั่งซื้อ (Admin)
    path('admin/orders/<int:pk>/delete/', views.admin_delete_order, name='admin-order-delete'), # หน้า ลบการสั่งซื้อ (Admin)
]

