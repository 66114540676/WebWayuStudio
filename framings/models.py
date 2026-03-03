from django.db import models
from django.conf import settings

class CustomFrameOrder(models.Model):
    # ==========================================
    # 1. กลุ่มตัวเลือก (Choices) - ประกาศตรงนี้ให้ครบก่อน
    # ==========================================
    
    # ตัวเลือกขนาด
    SIZE_CHOICES = [
        ('8x10', '8 x 10 นิ้ว'),
        ('10x12', '10 x 12 นิ้ว'),
        ('16x20', '16 x 20 นิ้ว'),
        ('20x24', '20 x 24 นิ้ว'),
        ('24x36', '24 x 36 นิ้ว'),
    ]
    
    # ตัวเลือกแบบกรอบ
    STYLE_CHOICES = [
        ('wood', 'กรอบไม้'),
        ('glass', 'กรอบกระจก'),
    ]

    # ตัวเลือกขาตั้ง
    MOUNTING_CHOICES = [
        ('stand', 'ขาตั้ง'),
        ('hanger', 'ที่แขวน'),
        ('both', 'ทั้งขาตั้งและที่แขวน'),
    ]

    # ตัวเลือกสถานะงาน
    STATUS_CHOICES = [
        ('pending', 'รอชำระเงิน'),
        ('processing', 'กำลังผลิต/เตรียมพัสดุ'),
        ('shipped', 'จัดส่งแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    # ตัวเลือกการจ่ายเงิน
    PAYMENT_CHOICES = [
        ('transfer', 'โอนเงินผ่านธนาคาร'),
    ]
    
    # ตัวเลือกการส่งของ
    SHIPPING_CHOICES = [
        ('pickup', 'รับเองที่ร้าน (ฟรี)'),
        ('standard', 'ขนส่งธรรมดา (50 บาท)'),
        ('express', 'ขนส่งด่วน (100 บาท)'),
    ]

    # ==========================================
    # 2. Fields เก็บข้อมูล (Columns)
    # ==========================================
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="ลูกค้า")
    uploaded_image = models.ImageField(upload_to='customer_framings_uploads/%Y/%m/', verbose_name="รูปจากลูกค้า")
    
    # ข้อมูลสินค้าที่เลือก
    size_option = models.CharField(max_length=10, choices=SIZE_CHOICES, verbose_name="ขนาด")
    style_option = models.CharField(max_length=20, choices=STYLE_CHOICES, default='wood', verbose_name="รูปแบบกรอบ") # <-- เพิ่มแล้ว
    mounting_option = models.CharField(max_length=10, choices=MOUNTING_CHOICES, verbose_name="การติดตั้ง")
    
    # ข้อมูลราคา/จำนวน
    quantity = models.PositiveIntegerField(default=1, verbose_name="จำนวน")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="ราคารวม")
    
    # ข้อมูลการชำระเงิน/จัดส่ง
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='transfer', verbose_name="วิธีชำระเงิน")
    shipping_method = models.CharField(max_length=10, choices=SHIPPING_CHOICES, default='standard', verbose_name="วิธีจัดส่ง")
    payment_slip = models.ImageField(upload_to='payment_slips_order_framings/%Y/%m/', null=True, blank=True, verbose_name="สลิปโอนเงิน")

    # เพิ่ม field หมายเหตุ
    note = models.TextField(blank=True, null=True, verbose_name="หมายเหตุเพิ่มเติม")

    # สถานะและเวลา
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สั่ง")
    
    @property
    def unit_price(self):
        # กำหนดราคาสินค้าตามขนาด (ควรตั้งให้ตรงกับที่คุณใช้คำนวณใน views.py)
        price_list = {
            '8x10': 150,
            '10x12': 200,
            '16x20': 600,
            '20x24': 800,
            '24x36': 1200,
        }
        # คืนค่าราคาตาม size_option ที่ลูกค้าเลือก
        return price_list.get(self.size_option, 0)
    # เพิ่มส่วนนี้เข้าไปครับ ^^^

    def __str__(self):
        return f"Order #{self.id} - {self.get_size_option_display()} ({self.get_status_display()})"