from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # <--- จำเป็นต้องใช้
from .forms import CustomMarblesOrderForm
from .models import CustomMarblesOrder
from django.contrib import messages

# 1. หน้าสั่งทำ (บังคับล็อกอิน)
@login_required(login_url='/accounts/login/') 
def create_order_marbles(request):
    if request.method == 'POST':
        form = CustomMarblesOrderForm(request.POST, request.FILES)
        if form.is_valid():
            # A. ดึงข้อมูลมาพักไว้ก่อน อย่าเพิ่ง save ลง DB
            order = form.save(commit=False)
            
            # B. ฝัง User ID ของคนที่ล็อกอินอยู่ลงไป
            order.user = request.user
            
            # C. บันทึกจริง
            order.save()

            # D. ส่งไปหน้า Checkout (ส่ง id ไปด้วย)
            return redirect('checkout_order_marbles', order_id=order.id) 
    else:
        form = CustomMarblesOrderForm()

    return render(request, 'marbles/create_order_marbles.html', {'form': form})

# 2. หน้า Checkout (เลือกส่ง + อัปสลิป)
@login_required
def checkout_order_marbles(request, order_id):
    order = get_object_or_404(CustomMarblesOrder, pk=order_id, user=request.user)

    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method')
        payment_slip = request.FILES.get('payment_slip')

        # คำนวณค่าส่ง
        shipping_cost = 0
        if shipping_method == 'standard':
            shipping_cost = 50
        elif shipping_method == 'express':
            shipping_cost = 100

        # ✅ บังคับแนบสลิปก่อน
        if not payment_slip:
            messages.error(request, "กรุณาแนบสลิปโอนเงินก่อนยืนยันการสั่งซื้อ")
            return redirect('checkout_order_marbles', order_id=order.id)

        # อัปเดตข้อมูล
        order.shipping_method = shipping_method
        order.final_price = (order.price or 0) + shipping_cost

        # ✅ เซฟสลิป + เปลี่ยนสถานะ
        order.PAYMENT_SLIP = payment_slip  # ถ้าฟิลด์จริงชื่อ payment_slip ให้เปลี่ยนเป็น order.payment_slip
        order.status = 'pending'

        order.save()
        return redirect('order_marbles_success')

    return render(request, 'marbles/checkout_order_marbles.html', {'order': order})

# 3. หน้าขอบคุณ (เพิ่มฟังก์ชันนี้เข้าไปครับ)
def order_marbles_success(request):
    # ใช้ไฟล์ html เดิม (thankyou.html) หรือจะเปลี่ยนชื่อไฟล์ html ก็ได้
    return render(request, 'marbles/order_marbles_success.html')

# 4. หน้า Manager (สำหรับแอดมิน)
# ควรใส่ @user_passes_test หรือเช็คว่าเป็น superuser ไหม เพื่อความปลอดภัย
def order_marbles_manager(request):
    orders = CustomMarblesOrder.objects.all().order_by('-created_at')
    total_sales = sum(order.price for order in orders if order.price)
    
    return render(request, 'marbles/admin/order_marbles_manager.html', {
        'orders': orders,
        'total_sales': total_sales
    })

# 5. อัปเดตสถานะ (สำหรับแอดมิน)
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(CustomMarblesOrder, pk=order_id)
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
    return redirect('order_marbles_manager')

# 6. ลบคำสั่งซื้อ (สำหรับแอดมิน)
def delete_marbles_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(CustomMarblesOrder, pk=order_id)
        order.delete()
    return redirect('order_marbles_manager')

# 7. แก้ไขคำสั่งซื้อ (สำหรับแอดมิน)
@login_required
def edit_order_marbles(request, order_id):
    order = get_object_or_404(CustomMarblesOrder, pk=order_id)
    
    if request.method == 'POST':
        # 1. รับค่าจาก Text Fields
        order.deceased_name = request.POST.get('deceased_name')
        
        # จัดการวันที่
        birth_date = request.POST.get('birth_date')
        order.birth_date = birth_date if birth_date else None
        
        death_date = request.POST.get('death_date')
        order.death_date = death_date if death_date else None
        
        # 2. รับค่า Specs
        order.size = request.POST.get('size')
        order.stone_style = request.POST.get('stone_style')
        
        # --- จุดที่แก้ไข (SAFE GUARD) ---
        # เช็คว่ามีค่าส่งมาไหม? ถ้ามีค่อยอัปเดต ถ้าไม่มี (เป็น None) ให้ข้ามไป (ใช้ค่าเดิมใน DB)
        
        new_status = request.POST.get('status')
        if new_status: 
            order.status = new_status

        new_shipping = request.POST.get('shipping_method')
        if new_shipping:
            order.shipping_method = new_shipping
            
        new_payment = request.POST.get('payment_method')
        if new_payment:
            order.payment_method = new_payment
            
        order.note = request.POST.get('note')
        # --------------------------------
        
        # 4. รับไฟล์รูปภาพ
        if request.FILES.get('deceased_photo'):
            order.deceased_photo = request.FILES.get('deceased_photo')
            
        if request.FILES.get('PAYMENT_SLIP'):
            order.PAYMENT_SLIP = request.FILES.get('PAYMENT_SLIP')

        order.save()
        messages.success(request, f"อัปเดตคำสั่งซื้อ #{order.id} เรียบร้อยแล้ว")
        return redirect('order_marbles_manager')

    context = {
        'order': order,
        'size_choices': CustomMarblesOrder.SIZE_CHOICES,
        'stone_style_choices': CustomMarblesOrder.STONE_STYLE_CHOICES,
        'shipping_choices': CustomMarblesOrder.SHIPPING_CHOICES,
        'payment_choices': CustomMarblesOrder.PAYMENT_CHOICES,
        'status_choices': CustomMarblesOrder.STATUS_CHOICES,
    }
    return render(request, 'marbles/admin/edit_order_marbles.html', context)