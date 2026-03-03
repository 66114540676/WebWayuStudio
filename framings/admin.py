from django.contrib import admin
from .models import CustomFrameOrder

class CustomFrameOrderAdmin(admin.ModelAdmin):
    # 1. รายการคอลัมน์ที่จะแสดงในหน้าตารางรวม
    list_display = [
        'id', 
        'user', 
        'size_option', 
        'style_option',
        'quantity',
        'total_price', 
        'payment_method',
        'status', 
        'created_at'
    ]
    
    # 2. ตัวกรองด้านขวามือ (ค้นหาจากสถานะ หรือ วันที่)
    list_filter = ['status', 'payment_method', 'shipping_method', 'created_at']
    
    # 3. ช่องค้นหา (Search) ด้านบน (ค้นหาจากชื่อลูกค้า หรือ เลข ID)
    search_fields = ['id', 'user__username', 'note']
    
    # 4. ทำให้แก้ไขสถานะได้จากหน้าตารางเลย (ไม่ต้องกดเข้าไปข้างใน)
    list_editable = ['status']
    
    # 5. เรียงลำดับจากใหม่ไปเก่า
    ordering = ['-created_at']

# ลงทะเบียน Model เข้ากับหน้า Admin
admin.site.register(CustomFrameOrder, CustomFrameOrderAdmin)