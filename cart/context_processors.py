from .models import Cart

# ✅ ตั้งชื่อฟังก์ชันว่า cart_count
def cart_count(request):
    count = 0
    
    # 1. เช็คว่า Login หรือยัง?
    if request.user.is_authenticated:
        # ถ้า Login แล้ว ให้ดึงตะกร้าของ User
        cart = Cart.objects.filter(user=request.user).first()
    else:
        # ถ้ายังไม่ Login ให้ดึงจาก Session
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = None

    if cart:
        # นับรวมจำนวนสินค้าทั้งหมด
        count = sum(item.quantity for item in cart.items.all())

    # ส่งตัวแปรชื่อ cart_item_count ไปให้ HTML
    return {'cart_item_count': count}