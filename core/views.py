from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView
from django.db.models import Sum
from django.db.models import Q

from django.utils import timezone
import calendar 

# --- Import Models ---
from accounts.models import CustomUser
from .models import WorkSchedule
# (ตรวจสอบชื่อ App ให้ถูกต้องตามโฟลเดอร์ของคุณ)
from stores.models import Order, Product
from framings.models import CustomFrameOrder  
from marbles.models import CustomMarblesOrder

User = get_user_model()

# ==========================================
# 1. Permissions & Mixins (ส่วนตรวจสอบสิทธิ์)
# ==========================================

# ฟังก์ชันเช็คว่าเป็น Staff หรือไม่ (ใช้กับ @user_passes_test)
def is_staff_check(user):
    return user.is_authenticated and user.is_staff

# Mixin สำหรับ Class-Based View (เช็คว่าเป็น Staff)
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_active

# ==========================================
# 2. General Views (หน้าหลัก & Dashboard)
# ==========================================

class HomePageView(TemplateView):
    template_name = "home.html"

class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # สถานะที่ถือว่าเป็นยอดขาย (เงินเข้า)
        paid_status = ['processing', 'shipped']

        # ==========================================
        # 1. ส่วนคำนวณยอดขาย "ทั้งหมด" (All Time)
        # ==========================================
        # ยอดเงิน (เฉพาะที่จ่ายแล้ว)
        sales_general = Order.objects.filter(status__in=paid_status).aggregate(sum=Sum('total_price'))['sum'] or 0
        sales_framing = CustomFrameOrder.objects.filter(status__in=paid_status).aggregate(sum=Sum('total_price'))['sum'] or 0
        sales_plaque = CustomMarblesOrder.objects.filter(status__in=paid_status).aggregate(sum=Sum('final_price'))['sum'] or 0

        grand_total = sales_general + sales_framing + sales_plaque

        count_store = Order.objects.count()
        count_frame = CustomFrameOrder.objects.count()
        count_marble = CustomMarblesOrder.objects.count()
    
        total_orders_count = count_store + count_frame + count_marble
        
        # ==========================================
        # 2. ส่วนคำนวณยอดขาย "เดือนนี้" (Monthly)
        # ==========================================
        now = timezone.localtime(timezone.now())
        _, last_day = calendar.monthrange(now.year, now.month)
        
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        # --- คำนวณยอดเงิน (เดือนนี้) ---
        m_sales_general = Order.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).aggregate(sum=Sum('total_price'))['sum'] or 0

        m_sales_framing = CustomFrameOrder.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).aggregate(sum=Sum('total_price'))['sum'] or 0

        m_sales_plaque = CustomMarblesOrder.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).aggregate(sum=Sum('final_price'))['sum'] or 0

        m_grand_total = m_sales_general + m_sales_framing + m_sales_plaque
        
        # --- คำนวณจำนวนออเดอร์ (เดือนนี้) ---
        # 🔴 เพิ่ม .exclude(status='cancelled') ไม่นับที่ยกเลิก
        m_count_general = Order.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).count()

        m_count_framing = CustomFrameOrder.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).count()

        m_count_plaque = CustomMarblesOrder.objects.filter(
            status__in=paid_status, 
            created_at__range=(start_date, end_date)
        ).count()

        m_total_orders = m_count_general + m_count_framing + m_count_plaque

        # ==========================================
        # 3. ส่วนนับจำนวนและสถานะ (Counts & Pending)
        # ==========================================
        
        # ✅ จำนวนออเดอร์แยกประเภท (ทั้งหมด - All Time)
        # 🔴 แก้ไขตรงนี้: ใส่ exclude('cancelled') เพื่อไม่ให้นับออเดอร์ที่ยกเลิก
        general_orders_count = Order.objects.exclude(status='cancelled').count()
        framing_orders_count = CustomFrameOrder.objects.exclude(status='cancelled').count()
        plaque_orders_count = CustomMarblesOrder.objects.exclude(status='cancelled').count()
        
        total_orders_count = general_orders_count + framing_orders_count + plaque_orders_count

        # ✅ รอตรวจสอบ (รวม)
        pending_count = (
            Order.objects.filter(status='pending').count() +
            CustomFrameOrder.objects.filter(status='pending').count() +
            CustomMarblesOrder.objects.filter(status='pending').count()
        )

        # ✅ รอตรวจสอบ (แยกประเภท)
        pending_general_count = Order.objects.filter(status='pending').count()
        pending_framing_count = CustomFrameOrder.objects.filter(status='pending').count()
        pending_plaque_count = CustomMarblesOrder.objects.filter(status='pending').count()

        # ✅ จำนวนผู้ใช้และสินค้า
        total_users_count = User.objects.count()
        total_products_count = Product.objects.count()

        # ส่งค่าไปยัง Template
        context.update({
            # --- ยอดขายรวม (All Time) ---
            'sales_general': sales_general,
            'sales_framing': sales_framing,
            'sales_plaque': sales_plaque,
            'grand_total': grand_total,

            # --- จำนวนออเดอร์รวม (All Time) ---
            'total_orders': total_orders_count,

            # 1. ชื่อสำหรับแสดงใน "กล่องการ์ดด้านบน" (ชื่อยาว)
            'general_orders_count': general_orders_count,
            'framing_orders_count': framing_orders_count,
            'plaque_orders_count': plaque_orders_count,

            # 2. ชื่อสำหรับแสดงใน "รายงานยอดขายด้านล่าง" (ชื่อสั้น - ของเดิม)
            'count_general': general_orders_count,
            'count_framing': framing_orders_count,
            'count_plaque': plaque_orders_count, 
            
            # --- ยอดขายเดือนนี้ (Monthly) ---
            'm_sales_general': m_sales_general,
            'm_sales_framing': m_sales_framing,
            'm_sales_plaque': m_sales_plaque,
            'm_grand_total': m_grand_total,
            'm_total_orders': m_total_orders,

            # ส่งจำนวนเดือนนี้ไปแสดงในกล่องเล็ก
            'm_count_general': m_count_general,
            'm_count_framing': m_count_framing,
            'm_count_plaque': m_count_plaque,

            # --- อื่นๆ ---
            'total_orders_count': total_orders_count,
            'pending_count': pending_count,
            'total_users_count': total_users_count,
            'total_products_count': total_products_count,
            'pending_general_count': pending_general_count,
            'pending_framing_count': pending_framing_count,
            'pending_plaque_count': pending_plaque_count,
        })

        return context



# ==========================================
# 3. User Management (จัดการผู้ใช้)
# ==========================================

class UserManageView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/admin_user_manage.html'
    context_object_name = 'users'
    ordering = ['-date_joined']
    paginate_by = 10  # (เผื่ออนาคต) แบ่งหน้าถ้าข้อมูลเยอะ

    # ✅ ส่วนที่เพิ่ม: ฟังก์ชันค้นหาข้อมูล
    def get_queryset(self):
        # ดึงข้อมูลทั้งหมดมาก่อน โดยเรียงตามวันที่สมัครล่าสุด
        queryset = super().get_queryset()
        
        # รับค่าที่ส่งมาจากช่องค้นหา (name="search")
        search_query = self.request.GET.get('search')
        
        if search_query:
            # กรองข้อมูลด้วย Q (OR condition)
            queryset = queryset.filter(
                Q(id__icontains=search_query) |          # ค้นหาด้วย ID
                Q(username__icontains=search_query) |    # ค้นหาด้วย Username
                Q(email__icontains=search_query) |       # ค้นหาด้วย Email
                Q(first_name__icontains=search_query) |  # ค้นหาด้วย ชื่อจริง
                Q(last_name__icontains=search_query)     # ค้นหาด้วย นามสกุล
            )
        
        return queryset

@user_passes_test(is_staff_check)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # ป้องกันไม่ให้แบนตัวเอง หรือ Superuser
    if user.is_superuser or user == request.user:
        messages.error(request, "ไม่สามารถระงับการใช้งานผู้ดูแลระบบสูงสุดหรือตัวเองได้")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "เปิดใช้งาน" if user.is_active else "ระงับการใช้งาน"
        name_display = getattr(user, 'username', user.email)
        messages.success(request, f"อัปเดตสถานะ {name_display} เป็น {status} แล้ว")
        
    return redirect('admin_user_manage')

@user_passes_test(is_staff_check)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.is_superuser or user == request.user:
        messages.error(request, "ไม่สามารถลบผู้ดูแลระบบสูงสุดหรือตัวเองได้")
    else:
        name_display = getattr(user, 'username', user.email)
        user.delete()
        messages.success(request, f"ลบผู้ใช้ {name_display} เรียบร้อยแล้ว")
        
    return redirect('admin_user_manage')

# ฟังก์ชันนี้ใช้ Superuser เท่านั้นเพื่อความปลอดภัย
@user_passes_test(lambda u: u.is_superuser)
def toggle_staff_status(request, user_id):
    # หมายเหตุ: เช็คให้แน่ใจว่าใช้ User หรือ CustomUser ให้ตรงกันทั้งไฟล์
    user = get_object_or_404(User, pk=user_id) 
    
    if user.is_staff:
        # ลดสถานะ (Staff -> คนธรรมดา)
        user.is_staff = False
        # ถ้า CustomUser มี field position ให้ใส่บรรทัดนี้
        if hasattr(user, 'position'): 
            user.position = "" 
        messages.warning(request, f'ลดสถานะ {user.username} เป็นผู้ใช้ทั่วไปแล้ว')
    else:
        # ตั้งเป็น Staff
        user.is_staff = True
        if hasattr(user, 'position'):
            user.position = "Staff" 
        messages.success(request, f'ตั้งค่า {user.username} เป็น Staff เรียบร้อยแล้ว')
        
    user.save()
    return redirect('admin_user_manage')

# ==========================================
# 4. Work Schedule / Calendar (ตารางงาน)
# ==========================================

# หน้าจัดการตารางงาน (ใช้ is_staff_check -> Staff ทุกคนเข้าได้)
@user_passes_test(is_staff_check)
def admin_calendar(request):
    events = WorkSchedule.objects.all().order_by('-start_date')
    
    if request.method == "POST":
        title = request.POST.get('title')
        date = request.POST.get('date')
        if title and date:
            WorkSchedule.objects.create(title=title, start_date=date)
            messages.success(request, f"เพิ่มคิวงาน '{title}' เรียบร้อยแล้ว")
            return redirect('admin_calendar')
            
    return render(request, 'admin/admin_calendar.html', {'events': events})

# บันทึกการแก้ไข (Update)
@user_passes_test(is_staff_check)
def edit_event(request, event_id):
    event = get_object_or_404(WorkSchedule, id=event_id)
    
    if request.method == "POST":
        title = request.POST.get('title')
        date = request.POST.get('date')
        
        if title and date:
            event.title = title
            event.start_date = date
            event.save()
            messages.success(request, f"แก้ไขงาน '{title}' เรียบร้อยแล้ว")
            
    return redirect('admin_calendar')

# ลบงาน
@user_passes_test(is_staff_check)
def delete_event(request, event_id):
    event = get_object_or_404(WorkSchedule, id=event_id)
    title = event.title
    event.delete()
    messages.success(request, f"ลบคิวงาน '{title}' เรียบร้อยแล้ว")
    return redirect('admin_calendar')

# API ส่งข้อมูล JSON ให้ปฏิทิน (ทุกคนดูได้)
def calendar_events(request):
    events = WorkSchedule.objects.all()
    data = []
    
    for event in events:
        display_title = event.title 

        # สี: Staff เห็นสีฟ้า, ลูกค้าเห็นสีเหลือง
        if request.user.is_staff:
            bg_color = '#3b82f6' 
            text_color = '#ffffff'
        else:
            bg_color = '#EAB308' 
            text_color = '#000000'

        data.append({
            'id': event.id,
            'title': display_title,
            'start': event.start_date.isoformat(),
            'color': bg_color,
            'textColor': text_color,
            'allDay': True 
        })
        
    return JsonResponse(data, safe=False)