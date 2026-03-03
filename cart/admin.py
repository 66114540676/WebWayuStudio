from django.contrib import admin
from .models import Cart, CartItem

# ลงทะเบียนให้ Model ไปโผล่ในหน้า Admin
admin.site.register(Cart)
admin.site.register(CartItem)