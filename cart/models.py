from django.db import models
from django.conf import settings  # ✅ 1. import settings มาแทน
from stores.models import Product 

class Cart(models.Model):
    # ✅ 2. ใช้ settings.AUTH_USER_MODEL แทน User ตรงๆ
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    session_key = models.CharField(max_length=40, null=True, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # ตรงนี้ต้องระวังนิดนึง ถ้า user เป็น None จะ error ถ้าเรียก .username
        # ใช้ logic นี้ปลอดภัยกว่าครับ
        username = self.user.username if self.user else 'Guest'
        return f"Cart {self.id} ({username})"

    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return self.quantity * self.product.price