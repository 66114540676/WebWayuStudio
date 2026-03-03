from django.contrib import admin
from .models import CustomMarblesOrder

class CustomMarblesOrderAdmin(admin.ModelAdmin):
    # 1. แสดงคอลัมน์อะไรบ้างในตารางหน้ารวม
    list_display = [
        'id', 
        'user', 
        'deceased_name', 
        'size', 
        'final_price', 
        'payment_method', 
        'status', 
        'created_at'
    ]
    
    # 2. ตัวกรองด้านขวามือ
    list_filter = ['status', 'payment_method', 'shipping_method', 'created_at']
    
    # 3. ช่องค้นหา (ค้นหาจาก ID, ชื่อผู้วายชนม์, หรือ Username ของลูกค้า)
    search_fields = ['id', 'deceased_name', 'user__username', 'note']
    
    # 4. แก้ไขสถานะงานได้ทันทีจากหน้าตาราง
    list_editable = ['status']
    
    # 5. จัดกลุ่มหน้าตาฟอร์มแก้ไข (เพื่อให้ดูง่าย ไม่ยาวพรืดลงมา)
    fieldsets = (
        ('ข้อมูลลูกค้า', {
            'fields': ('user', 'note')
        }),
        ('ข้อมูลผู้วายชนม์ (บนป้าย)', {
            'fields': ('deceased_name', 'deceased_photo', 'birth_date', 'death_date')
        }),
        ('รายละเอียดการผลิต', {
            'fields': ('stone_style', 'size', 'price', 'shipping_method', 'final_price')
        }),
        ('การชำระเงินและสถานะ', {
            'fields': ('payment_method', 'PAYMENT_SLIP', 'status', 'created_at')
        }),
    )
    
    # ทำให้ field วันที่สร้าง แก้ไขไม่ได้ (กันพลาด)
    readonly_fields = ['created_at']

# ลงทะเบียน Model
admin.site.register(CustomMarblesOrder, CustomMarblesOrderAdmin)