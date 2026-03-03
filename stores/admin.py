from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# --- ส่วนจัดการสินค้าและหมวดหมู่ ---

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'updated_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock'] # แก้ราคาและสต็อกได้จากหน้าตารางเลย

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'updated_at']
    prepopulated_fields = {'slug': ('name',)} # สร้าง slug อัตโนมัติตอนพิมพ์ชื่อ

# --- ส่วนจัดการ Order (ไฮไลท์สำคัญ) ---

# สร้างตารางสินค้าย่อย เพื่อให้โชว์ในหน้า Order หลัก
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price_show']

    def total_price_show(self, obj):
        if obj.price and obj.quantity:
            return obj.price * obj.quantity
        return 0
    
    total_price_show.short_description = "รวมราคา"

class OrderAdmin(admin.ModelAdmin):
    # คอลัมน์ที่จะโชว์ในหน้ารวม
    list_display = [
        'id', 
        'customer', 
        'total_price', 
        'payment_method', 
        'shipping_method',
        'status', 
        'created_at'
    ]
    
    # ตัวกรองด้านขวา
    list_filter = ['status', 'payment_method', 'created_at']
    
    # ช่องค้นหา (หาจากชื่อลูกค้า หรือ เลข Order)
    search_fields = ['id', 'customer__username', 'customer__first_name']
    
    # แก้สถานะได้ทันทีจากหน้าตาราง
    list_editable = ['status']
    
    # เอาตารางสินค้า (OrderItem) มาแปะในหน้านี้
    inlines = [OrderItemInline]
    
    # เรียงลำดับจากใหม่ไปเก่า
    ordering = ['-created_at']

# ลงทะเบียนเข้าสู่ระบบ Admin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem) # ไม่ต้องลงแยก เพราะไปโผล่ใน Order แล้ว