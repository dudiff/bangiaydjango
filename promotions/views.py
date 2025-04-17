from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from .models import Promotion

@login_required
def apply_promotion(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            promotion = Promotion.objects.get(code=code)
            cart = Cart.get_active_cart(request.user)
            
            is_valid, message = promotion.is_valid(cart.get_total())
            
            if is_valid:
                cart.promotion = promotion
                cart.discount = promotion.calculate_discount(cart.get_total())
                cart.save()
                
                # Increment times used
                promotion.times_used += 1
                promotion.save()
                
                messages.success(request, 'Áp dụng mã giảm giá thành công!')
            else:
                messages.error(request, message)
                
        except Promotion.DoesNotExist:
            messages.error(request, 'Mã giảm giá không tồn tại')
            
    return redirect('cart:cart')

@login_required
def remove_promotion(request):
    if request.method == "POST":
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if cart and cart.promotion:
            promotion = cart.promotion
            # Reset cart promotion and discount
            cart.promotion = None
            cart.discount = 0
            cart.save()
            
            # Decrement times_used
            if promotion.times_used > 0:
                promotion.times_used -= 1
                promotion.save()
                
            messages.success(request, f"Đã xóa mã giảm giá {promotion.code}")
        else:
            messages.error(request, "Không tìm thấy mã giảm giá trong giỏ hàng.")
    return redirect('cart:cart')
