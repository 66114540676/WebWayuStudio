from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserUpdateForm, UserLoginForm
from django.db import IntegrityError

from stores.models import Order
from framings.models import CustomFrameOrder 
from marbles.models import CustomMarblesOrder

# ==========================================
# 1. ส่วนจัดการการเข้าสู่ระบบและสมัครสมาชิก (Authentication)
# ==========================================

# --- ส่วนการล็อกอิน ---
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            # --- ตรวจสอบกรณีโดนแบน ---
            username = request.POST.get('username')
            password = request.POST.get('password')
            User = get_user_model()
            
            user_check = User.objects.filter(username=username).first()

            if user_check:
                # ถ้ารหัสถูก แต่สถานะไม่ Active (โดนแบน)
                if user_check.check_password(password) and not user_check.is_active:
                    messages.error(request, "บัญชีของคุณถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ")
                    
                    # +++ จุดที่แก้ไข: ล้างฟอร์มให้เป็นฟอร์มเปล่า เพื่อลบ Error สีแดงด้านล่างทิ้ง +++
                    form = UserLoginForm() 
            # (ถ้าไม่ใช่เคสโดนแบน ก็ให้มันใช้ form ตัวเดิมที่มี Error แจ้งเตือนรหัสผิดปกติ)
            
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# --- ส่วนการล็อกเอาท์ ---
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

# --- ส่วนการสมัครสมาชิก ---
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

# ==========================================
# 2. ส่วนจัดการโปรไฟล์และข้อมูลส่วนตัว (User Profile Management)
# ==========================================

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'โปรไฟล์ของคุณถูกอัปเดตเรียบร้อยแล้ว!')
            return redirect('profile')

    else:
        form = CustomUserUpdateForm(instance=request.user)

    context = {
        'form': form 
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'รหัสผ่านของคุณถูกเปลี่ยนเรียบร้อยแล้ว!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


# ==========================================
# 3. ส่วนจัดการประวัติการสั่งซื้อ (Order History & Dashboard)
# ==========================================

@login_required
def order_history_dashboard(request):
    """แสดงหน้า Dashboard ให้เลือกประเภท"""
    return render(request, 'accounts/order_history_dashboard.html')

@login_required
def order_history(request, order_type):
    context = {}
    current_status = request.GET.get('status', 'all')

    if order_type == 'products':
        page_title = "รายการสั่งซื้อสินค้า"
        template_name = 'stores/order_history_stores.html'
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')

    elif order_type == 'framings':
        page_title = "รายการสั่งทำกรอบรูป"
        template_name = 'framings/order_history_framings.html'

        # ✅ ซ่อน draft ออกจากประวัติ
        orders = CustomFrameOrder.objects.filter(user=request.user).exclude(status__iexact='draft').order_by('-created_at')

    elif order_type == 'marbles':
        page_title = "รายการสั่งทำป้ายหินอ่อน"
        template_name = 'marbles/order_history_marbles.html'

        # ✅ (ถ้าป้ายหินอ่อนมี draft ด้วย ก็ซ่อนเหมือนกัน)
        orders = CustomMarblesOrder.objects.filter(user=request.user).exclude(status__iexact='draft').order_by('-created_at')

    else:
        return redirect('order_history_dashboard')

    # 2. Logic กรองสถานะ (เหมือนเดิม)
    if current_status != 'all':
        orders = orders.filter(status__iexact=current_status)

    context = {
        'orders': orders,
        'page_title': page_title,
        'order_type': order_type,
        'current_status': current_status
    }

    return render(request, template_name, context)


# ==========================================
# 4. ส่วนแสดงรายละเอียดการสั่งซื้อแต่ละประเภท (Order Details)
# ==========================================

@login_required
def product_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'stores/order_stores_detail.html', {'order': order})

@login_required
def framing_order_detail(request, order_id):
    order = get_object_or_404(CustomFrameOrder, id=order_id, user=request.user)
    return render(request, 'framings/order_framing_detail.html', {'order': order})

@login_required
def marbles_order_detail(request, order_id):
    order = get_object_or_404(CustomMarblesOrder, id=order_id, user=request.user)
    return render(request, 'marbles/order_marbles_detail.html', {'order': order})