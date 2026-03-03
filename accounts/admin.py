from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['username', 'email', 'phone_number', 'is_staff']

    fieldsets = UserAdmin.fieldsets + (
        ('ข้อมูลเพิ่มเติม', {'fields': ('image', 'phone_number', 'address',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ข้อมูลเพิ่มเติม', {'fields': ('image', 'phone_number', 'address',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)