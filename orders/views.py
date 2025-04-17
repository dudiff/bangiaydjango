from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from .models import Order
from shipping.models import City, District, Ward
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def create_order(request):
    cart = Cart.get_active_cart(request.user)
    if not cart:
        messages.error(request, 'Giỏ hàng trống')
        return redirect('cart:cart')

    # Get shipping address from session
    shipping_data = {
        'full_name': request.session.get('selectedFullName'),
        'email': request.session.get('selectedEmail'),
        'phone': request.session.get('selectedPhone'),
        'city_id': request.session.get('selectedCity'),
        'district_id': request.session.get('selectedDistrict'),
        'ward_id': request.session.get('selectedWard'),
        'address': request.session.get('selectedAddress'),
    }

    try:
        city = City.objects.get(id=shipping_data['city_id'])
        district = District.objects.get(id=shipping_data['district_id'])
        ward = Ward.objects.get(id=shipping_data['ward_id'])
        
        shipping_address = (
            f"Họ và tên: {shipping_data['full_name']}\n"
            f"Email: {shipping_data['email']}\n"
            f"Số điện thoại: {shipping_data['phone']}\n"
            f"Địa chỉ: {shipping_data['address']}\n"
            f"Phường/Xã: {ward.name_with_type}\n"
            f"Quận/Huyện: {district.name_with_type}\n"
            f"Tỉnh/Thành phố: {city.name_with_type}"
        ).strip()

        # Calculate total amount including shipping
        total_amount = float(cart.get_total())
        shipping_fee = float(cart.shipping_fee or 0)
        final_total = total_amount + shipping_fee

        # Create order with complete shipping information
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            shipping_name=shipping_data['full_name'],  # Changed from customer_name
            shipping_email=shipping_data['email'],     # Changed from customer_email
            shipping_phone=shipping_data['phone'],     # Changed from customer_phone
            shipping_city=city,                        # Added city reference
            shipping_district=district,                # Added district reference
            shipping_ward=ward,                        # Added ward reference
            total_amount=total_amount,
            shipping_fee=shipping_fee
        )
        
        # Store order total in session for payment processing
        request.session['order_total_with_shipping'] = float(final_total)
        request.session['current_order_id'] = order.id
        request.session.modified = True
        
        # Clear shipping session data
        shipping_keys = [
            'selectedFullName', 'selectedEmail', 'selectedPhone',
            'selectedCity', 'selectedDistrict', 'selectedWard', 
            'selectedAddress'
        ]
        for key in shipping_keys:
            if key in request.session:
                del request.session[key]
        
        return render(request, 'orders/create_order.html', {'order': order})
        
    except (City.DoesNotExist, District.DoesNotExist, Ward.DoesNotExist):
        messages.error(request, 'Thông tin địa chỉ không hợp lệ')
        return redirect('checkout:information')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'partials/orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'partials/orders/order_detail.html', {'order': order})

@login_required
def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Get order items
    items = order.order_items.all()
    
    # Calculate final total
    final_total = order.total_amount + order.shipping_fee
    
    context = {
        'order': order,
        'order_items': items,
        'final_total': final_total
    }
    return render(request, 'admin/orders/order_print.html', context)


# When processing VNPAY payment, use:
# CORRECT: Use cart's method before creating order
# amount = cart.get_total_with_shipping()

# OR after creating order, use the stored total_amount:
# CORRECT: Use order's total_amount field
# amount = order.total_amount

# INCORRECT: Don't try to call this method on Order
# amount = order.get_total_with_shipping()  # This will cause the error


@login_required
@require_POST
def confirm_delivery(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status == 'shipping':  # Changed from 'shipped' to 'shipping'
            order.status = 'delivered'
            if order.payment_method == 'cod':
                order.payment_status = 'paid'
            order.save()
            return JsonResponse({
                'success': True,
                'message': 'Cảm ơn bạn đã xác nhận! Đơn hàng đã được giao thành công.'
            })
        return JsonResponse({
            'success': False,
            'message': 'Đơn hàng chưa được giao, không thể xác nhận'
        })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng'
        })

@login_required
@require_POST
def confirm_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.payment_method == 'cod' and order.status == 'delivered':
            order.payment_status = 'paid'
            order.save()
            return JsonResponse({
                'success': True,
                'message': 'Đã xác nhận thanh toán thành công'
            })
        return JsonResponse({
            'success': False,
            'message': 'Không thể xác nhận thanh toán cho đơn hàng này'
        })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng'
        })
@login_required
@require_POST
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.cancel_order():
            return JsonResponse({
                'success': True,
                'message': 'Đơn hàng đã được huỷ thành công'
            })
        return JsonResponse({
            'success': False,
            'message': 'Không thể huỷ đơn hàng này'
        })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy đơn hàng'
        })