from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CustomFrameOrder
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

PRICE_LIST = {
    '8x10': 150,   # ขนาด 8x10 นิ้ว = 150 บาท
    '10x12': 200,    # ขนาด 10x12 = 400 บาท
    '16x20': 600,    # ขนาด 16x20 = 600 บาท
    '20x24': 800,    # ขนาด 20x24 = 800 บาท
    '24x36': 1200,   # ขนาด 24x36 = 1200 บาท
    '25x38': 1500,   # ขนาด 25x38 = 1500 บาท
}

# Mixin สำหรับตรวจสอบสิทธิ์ผู้ใช้ว่าเป็นเจ้าหน้าที่ (Staff) และบัญชีสถานะปกติหรือไม่
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_active

# ฟังก์ชันสำหรับสร้างคำสั่งซื้อใหม่ (ขั้นตอนแรก: อัปโหลดรูปและเลือกขนาดกรอบรูป)
@login_required(login_url='/accounts/login/')
def create_order_framings(request):
    if request.method == 'POST':
        uploaded_image = request.FILES.get('image')
        size = request.POST.get('size_option')
        style = request.POST.get('style_option')      
        mounting = request.POST.get('mounting_option')
        
        # [เพิ่ม] รับค่าหมายเหตุจากฟอร์ม
        note = request.POST.get('note', '') 

        estimated_price = PRICE_LIST.get(size, 0)

        # สร้าง Order เบื้องต้น
        order = CustomFrameOrder.objects.create(
            user=request.user if request.user.is_authenticated else None,
            uploaded_image=uploaded_image,
            size_option=size,
            style_option=style,         
            mounting_option=mounting,
            note=note,  # [เพิ่ม] บันทึกหมายเหตุลงฐานข้อมูล
            total_price=estimated_price,
            status='draft'
        )

        return redirect('checkout_order_framings', order_id=order.id)

    return render(request, 'framings/create_order_framings.html')

# ฟังก์ชันสำหรับหน้าชำระเงินและระบุการจัดส่ง (ขั้นตอนที่สอง: คำนวณราคารวมและอัปโหลดสลิป)
def checkout_order_framings(request, order_id):
    order = get_object_or_404(CustomFrameOrder, id=order_id)

    if request.method == 'POST':
        # รับค่าการจัดส่งและจ่ายเงิน
        shipping_method = request.POST.get('shipping_method')
        payment_method = request.POST.get('payment_method')
        uploaded_slip = request.FILES.get('payment_slip')

        # รับค่าจำนวนสินค้า (Quantity)
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1: quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        # คำนวณค่าส่ง
        if shipping_method == 'pickup':
            shipping_cost = 0          # รับเอง ฟรี
        elif shipping_method == 'express':
            shipping_cost = 100        # ด่วน 100
        else:
            shipping_cost = 50         # ธรรมดา 50 (standard)

        # คำนวณราคารวมใหม่
        unit_price = PRICE_LIST.get(order.size_option, 0)
        
        # สูตร: (ราคาต่อชิ้น x จำนวน) + ค่าส่ง
        grand_total = (unit_price * quantity) + shipping_cost

        # บันทึกอัปเดตข้อมูลลง Database
        order.quantity = quantity
        order.shipping_method = shipping_method
        order.payment_method = payment_method
        order.total_price = grand_total

        # ถ้าโอนเงิน ต้องแนบสลิป
        if payment_method == 'transfer':
            if uploaded_slip:
                order.payment_slip = uploaded_slip
            else:
                messages.error(request, "กรุณาแนบสลิปโอนเงิน")
                return redirect('checkout_order_framings', order_id=order.id)
        
        order.status = 'pending' 
        order.save()
        
        return redirect('order_framings_success')

    return render(request, 'framings/checkout_order_framings.html', {'order': order})

# ฟังก์ชันแสดงหน้าแจ้งผลเมื่อทำการสั่งซื้อเสร็จสมบูรณ์
def order_framings_success(request):
    return render(request, 'framings/order_framings_success.html')

# Class View สำหรับหน้าจัดการคำสั่งซื้อทั้งหมด (สำหรับผู้ดูแลระบบเท่านั้น)
class ShopManagerView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomFrameOrder
    template_name = 'framings/admin/order_framings_manager.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_active
    
# ฟังก์ชันสำหรับอัปเดตสถานะของคำสั่งซื้อ (เช่น รอตรวจสอบ -> ดำเนินการ)
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(CustomFrameOrder, id=order_id)
    new_status = request.POST.get('status')
    order.status = new_status
    order.save()
    return redirect('order_framings_manager')

# ฟังก์ชันสำหรับลบคำสั่งซื้อออกจากระบบ
@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(CustomFrameOrder, id=order_id)
    order.delete()
    return redirect('order_framings_manager')

# ฟังก์ชันสำหรับแก้ไขรายละเอียดคำสั่งซื้อและคำนวณราคาใหม่ (สำหรับผู้ดูแลระบบ)
@login_required
def edit_order_framings(request, order_id):
    order = get_object_or_404(CustomFrameOrder, id=order_id)

    if request.method == 'POST':
        # ... (รับค่าอื่นๆ เหมือนเดิม) ...
        
        # 1. รับค่าที่ส่งผลต่อราคา
        order.size_option = request.POST.get('size_option')
        order.shipping_method = request.POST.get('shipping_method')
        
        try:
            order.quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            order.quantity = 1

        # 2. คำนวณราคาใหม่ (Logic เดียวกับตอนสร้าง Order)
        # ตารางราคา (ควรตรงกับ Models)
        price_list = {
            '8x10': 150,
            '10x12': 200,
            '16x20': 600,
            '20x24': 800,
            '24x36': 1200,
            '25x38': 1500,
        }
        unit_price = price_list.get(order.size_option, 0)
        
        # ค่าส่ง
        shipping_cost = 0
        if order.shipping_method == 'standard':
            shipping_cost = 50
        elif order.shipping_method == 'express':
            shipping_cost = 100
            
        # 3. เซ็ตราคารวมใหม่
        order.total_price = (unit_price * order.quantity) + shipping_cost

        # ... (รับค่าอื่นๆ ต่อ status, payment etc.) ...
        
        order.save()
        messages.success(request, f"บันทึกและคำนวณราคาใหม่เรียบร้อย (ยอดสุทธิ: {order.total_price} บาท)")
        return redirect('order_framings_manager')
            
    # ส่ง Context
    context = {
        'order': order,
        'status_choices': CustomFrameOrder.STATUS_CHOICES,
        'size_choices': CustomFrameOrder.SIZE_CHOICES,
        'style_choices': CustomFrameOrder.STYLE_CHOICES,
        'mounting_choices': CustomFrameOrder.MOUNTING_CHOICES,
        'payment_choices': CustomFrameOrder.PAYMENT_CHOICES,
        'shipping_choices': CustomFrameOrder.SHIPPING_CHOICES,
    }
    
    return render(request, 'framings/admin/edit_order_framings.html', context)