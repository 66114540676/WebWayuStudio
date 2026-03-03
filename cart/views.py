from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from stores.models import Product 
from .models import Cart, CartItem 

# --- ฟังก์ชันช่วยเหลือ (Helper Function) ---
def _get_or_create_cart(request):
    """
    ฟังก์ชันดึงตะกร้าสินค้า
    - ถ้า Login แล้ว: จะดึงตะกร้าที่ผูกกับ User
    - ถ้ายังไม่ Login: จะดึงตะกร้าที่ผูกกับ Session
    """
    # 1. กรณีลูกค้า Login อยู่
    if request.user.is_authenticated:
        # ค้นหาตะกร้าของ User นี้
        # (ใช้ .filter().first() เพื่อป้องกัน error กรณีมีหลายใบ และเอาใบแรกสุดมาใช้)
        cart = Cart.objects.filter(user=request.user).first()
        
        # ถ้ายังไม่มีตะกร้าของ User ให้สร้างใหม่
        if not cart:
            cart = Cart.objects.create(user=request.user)
            
        return cart

    # 2. กรณีลูกค้าทั่วไป (Guest) ยังไม่ Login
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # ค้นหาตะกร้าจาก Session
        try:
            cart = Cart.objects.get(session_key=session_key)
            # ถ้าเจอตะกร้า แต่ตะกร้านั้นมีเจ้าของไปแล้ว (User อื่น) ให้สร้างใหม่
            if cart.user: 
                cart = Cart.objects.create(session_key=session_key)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(session_key=session_key)
            
        return cart

# ----------------------------------------------
# --- R (Read): แสดงหน้าตะกร้าสินค้า ---
# ----------------------------------------------
@login_required(login_url='login')
def cart_detail(request):
    """แสดงรายการสินค้าทั้งหมดที่อยู่ในตะกร้าปัจจุบันของผู้ใช้"""
    cart = _get_or_create_cart(request)
    
    # ดึงรายการสินค้าทั้งหมดในตะกร้า
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    # ✅ คำนวณราคารวมที่นี่ (แก้ปัญหาราคาไม่ขึ้น)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price, # ส่งตัวแปรนี้ไปใช้ใน Template ได้เลย
    }
    return render(request, 'cart/cart_stores_detail.html', context)

# ----------------------------------------------
# --- C (Create): เพิ่มสินค้าลงในตะกร้า ---
# ----------------------------------------------
@login_required(login_url='login')
@require_POST
def add_to_cart(request, product_id):
    cart = _get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # ✅ เพิ่มท่อนนี้ครับ: ถ้า Login อยู่ และตะกร้านี้ยังไม่มีเจ้าของ ให้ยึดเป็นของ User นี้เลย
    if request.user.is_authenticated and not cart.user:
        cart.user = request.user
        cart.save()
    
    # ... (ส่วนดึง quantity และ create CartItem ด้านล่าง เหมือนเดิมไม่ต้องแก้) ...
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0: quantity = 1
    except ValueError:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"อัปเดตจำนวน {product.name} แล้ว")
    else:
        messages.success(request, f"เพิ่ม {product.name} ลงตะกร้าเรียบร้อย")

    return redirect('cart:cart_detail')

# ----------------------------------------------
# --- U (Update): แก้ไขจำนวนสินค้าในตะกร้า ---
# ----------------------------------------------
@login_required(login_url='login')
@require_POST
def update_cart(request, item_id):
    cart = _get_or_create_cart(request)
    # ต้องเช็คว่าเป็น item ในตะกร้าเราจริงไหม
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    try:
        new_quantity = int(request.POST.get('quantity', 0))
    except ValueError:
        new_quantity = 0

    if new_quantity > 0:
        # ✅ เช็คสต็อกก่อนบันทึก
        if new_quantity > cart_item.product.stock:
            new_quantity = cart_item.product.stock
            messages.warning(request, f"สินค้ามีจำกัดเพียง {cart_item.product.stock} ชิ้น")
        
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, "อัปเดตจำนวนสินค้าแล้ว")
    else:
        cart_item.delete() 
        messages.warning(request, "ลบสินค้าออกจากตะกร้าแล้ว")
        
    return redirect('cart:cart_detail')

# ----------------------------------------------
# --- D (Delete): ลบรายการสินค้าออกจากตะกร้า ---
# ----------------------------------------------
@login_required(login_url='login')
@require_POST
def remove_from_cart(request, item_id):
    """ลบรายการสินค้า (CartItem) ออกจากตะกร้า"""
    cart = _get_or_create_cart(request)
    
    # ✅ Security: ต้องลบเฉพาะของในตะกร้าตัวเองเท่านั้น
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    cart_item.delete()
    messages.success(request, "ลบสินค้าเรียบร้อยแล้ว")
    
    return redirect('cart:cart_detail')