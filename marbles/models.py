from django.db import models
from django.conf import settings  # <--- จำเป็นต้อง import เพื่อเรียกใช้ Custom User

class CustomMarblesOrder(models.Model):
    # --- 1. ตัวเลือกต่างๆ (Choices) ---
    SIZE_CHOICES = [
        ('15x20', '15x20 ซม. (1,000 บาท)'),
        ('14x29', '14x29 ซม. (1,700 บาท)'),
        ('20x30', '20x30 ซม. (2,500 บาท)'),
    ]

    STONE_STYLE_CHOICES = [
        ('black_granite', 'หินแกรนิตดำ'),
        ('white_marble', 'หินอ่อนขาว'),
        ('red_granite', 'หินแกรนิตแดง'),
    ]

    STATUS_CHOICES = [
        ('pending', 'รอชำระเงิน'),
        ('processing', 'กำลังผลิต/เตรียมพัสดุ'),
        ('shipped', 'จัดส่งแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    SHIPPING_CHOICES = [
        ('pickup', 'รับเองที่ร้าน (ฟรี)'),
        ('standard', 'ขนส่งธรรมดา (50 บาท)'),
        ('express', 'ขนส่งด่วน (100 บาท)'),
    ]

    PAYMENT_CHOICES = [
        ('transfer', 'โอนเงินผ่านธนาคาร'),
    ]

    # --- 2. ข้อมูลลูกค้า (แก้ไขใหม่) ---
    # เชื่อมโยงกับ User ID (Custom User) แทนการกรอกชื่อ
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="ผู้สั่งทำ (User ID)",
        null=True, blank=True
    )
    # (ลบ customer_name และ customer_tel ออกแล้ว)

    # --- 3. ข้อมูลบนป้าย ---
    deceased_name = models.CharField(max_length=200, verbose_name="ชื่อผู้วายชนม์ (บนป้าย)")
    deceased_photo = models.ImageField(upload_to='customer_marbles_uploads/%Y/%m/', verbose_name="รูปถ่าย")
    birth_date = models.DateField(verbose_name="วัน/เดือน/ปีเกิด", blank=True, null=True)
    death_date = models.DateField(verbose_name="วัน/เดือน/ปีมรณะ", blank=True, null=True)

    # --- 4. รายละเอียดการผลิต ---
    stone_style = models.CharField(max_length=50, choices=STONE_STYLE_CHOICES, verbose_name="รูปแบบหิน")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='15x20', verbose_name="ขนาด")
    note = models.TextField(verbose_name="หมายเหตุเพิ่มเติม", blank=True, null=True)

    # --- 5. การชำระเงินและการจัดส่ง ---
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='transfer', verbose_name="วิธีชำระเงิน")
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='pickup', verbose_name="วิธีจัดส่ง")
    PAYMENT_SLIP = models.ImageField(upload_to='payment_slips_order_marbles/%Y/%m/', verbose_name="สลิปโอนเงิน", blank=True, null=True)
    
    # --- 6. ราคาและสถานะ ---
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาป้าย (บาท)", blank=True, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาสุทธิ (รวมส่ง)", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สั่ง")

    def save(self, *args, **kwargs):
        # 1. คำนวณราคาป้ายตามขนาด
        if self.size == '15x20':
            self.price = 1000
        elif self.size == '14x29':
            self.price = 1700
        elif self.size == '20x30':
            self.price = 2500
        else:
            self.price = 0

        # 2. คำนวณค่าส่ง (เผื่อกรณีมีการแก้ไขในหน้า Admin จะได้คำนวณถูกเสมอ)
        shipping_cost = 0
        if self.shipping_method == 'standard':
            shipping_cost = 50
        elif self.shipping_method == 'express':
            shipping_cost = 100
        
        # 3. รวมเป็นราคาสุทธิ
        self.final_price = self.price + shipping_cost

        super().save(*args, **kwargs)

    def __str__(self):
        # เปลี่ยนการแสดงผลให้โชว์ User
        username = self.user.username if self.user else "Guest"
        return f"#{self.id} {self.deceased_name} (โดย: {username})"

    class Meta:
        verbose_name = "รายการสั่งทำป้าย"
        verbose_name_plural = "รายการสั่งทำป้ายทั้งหมด"