from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal

# --- 1. Model หมวดหมู่ (Category) ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ชื่อหมวดหมู่")
    
    # แก้ไข field นี้ ให้ 'blank=True' เพื่ออนุญาตให้เราเว้นว่างได้
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, blank=True)
    
    # --- 2. เพิ่ม 4 field นี้ ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาสร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="เวลาแก้ไขล่าสุด")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(class)s_created', # %(class)s จะกลายเป็น 'category_created'
        editable=False, verbose_name="สร้างโดย"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(class)s_updated', # %(class)s จะกลายเป็น 'category_updated'
        editable=False, verbose_name="แก้ไขล่าสุดโดย"
    )

    class Meta:
        verbose_name = "หมวดหมู่"
        verbose_name_plural = "หมวดหมู่"

    def __str__(self):
        return self.name
    
    # --- 2. เพิ่มฟังก์ชัน 'save' นี้เข้าไป ---
    def save(self, *args, **kwargs):
        # ถ้าช่อง slug ยังว่างอยู่ (หรือเป็นการสร้างใหม่)
        if not self.slug:
            # ให้สร้าง slug อัตโนมัติจาก 'name' (และอนุญาตภาษาไทย)
            self.slug = slugify(self.name, allow_unicode=True)
        
        # รันคำสั่ง save ตามปกติ
        super().save(*args, **kwargs)

# --- 2. Model สินค้า (Product) ---
class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="หมวดหมู่"
    )
    name = models.CharField(max_length=200, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="รายละเอียดสินค้า")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาสินค้า") 
    stock = models.IntegerField(default=0, verbose_name="จำนวนคงเหลือ")
    image = models.ImageField(upload_to='products/%Y/%m/', null=True, blank=True, verbose_name="รูปสินค้า")
    
    # --- 2. เพิ่ม 4 field เดียวกันนี้ ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาสร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="เวลาแก้ไขล่าสุด")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(class)s_created', # %(class)s จะกลายเป็น 'product_created'
        editable=False, verbose_name="สร้างโดย"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(class)s_updated', # %(class)s จะกลายเป็น 'product_updated'
        editable=False, verbose_name="แก้ไขล่าสุดโดย"
    )
    
    class Meta:
        verbose_name = "สินค้า"
        verbose_name_plural = "สินค้า"

    def __str__(self):
        return self.name

# --- 3. Model คำสั่งซื้อ (Order) ---
class Order(models.Model):
    SHIPPING_CHOICES = [
        ('pickup', 'รับเองที่ร้าน (ฟรี)'),
        ('standard', 'ขนส่งธรรมดา (50 บาท)'),
        ('express', 'ขนส่งด่วน (100 บาท)'),
    ]

    PAYMENT_CHOICES = [
        ('transfer', 'โอนเงินผ่านธนาคาร'),
    ]

    STATUS_CHOICES = [
        ('pending', 'รอชำระเงิน'),
        ('processing', 'กำลังผลิต/เตรียมพัสดุ'),
        ('shipped', 'จัดส่งแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="ลูกค้า",
    )

    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='pickup')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ยอดสุทธิ")

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES,default='transfer', verbose_name="วิธีชำระเงิน")
    payment_slip = models.ImageField(upload_to='payment_oader_slips/%Y/%m/', null=True, blank=True, verbose_name="สลิปโอนเงิน")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาสร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="เวลาแก้ไขล่าสุด")

    class Meta:
        verbose_name = "คำสั่งซื้อ"
        verbose_name_plural = "คำสั่งซื้อ"

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="สินค้า")
    quantity = models.PositiveIntegerField(verbose_name="จำนวน")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาต่อชิ้น (ณ ตอนซื้อ)")

    class Meta:
        verbose_name = "รายการสินค้าในบิล"
        verbose_name_plural = "รายการสินค้าในบิล"

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    @property
    def total_price(self):
        return self.price * self.quantity