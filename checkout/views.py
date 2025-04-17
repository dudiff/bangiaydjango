# At the top of the file, organize imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.urls import reverse
# Combine all model imports into a single block
from cart.models import Cart
from orders.models import Order, OrderItem  # Import OrderItem here if needed
from shipping.models import (
    ShippingFee, 
    City, 
    District, 
    Ward, 
    ShippingInfo
)

# Standard library imports
import datetime
import hashlib
import urllib.parse
import time
import hmac
import tempfile
import json
import requests
import uuid

@login_required
def checkout_information(request):
    # Check if user has a profile
    try:
        profile = request.user.profile
    except:
        messages.warning(request, "Vui lòng cập nhật thông tin cá nhân trước khi tiến hành thanh toán.")
        return redirect('userauths:profile')

    # Use get_active_cart instead of get_cart
    cart = Cart.get_active_cart(request.user)
    if not cart or not cart.items.exists():
        messages.warning(request, "Giỏ hàng của bạn đang trống.")
        return redirect('cart:cart')

    # Get saved address from session if exists
    saved_city_id = request.session.get('shipping_city_id')
    saved_district_id = request.session.get('shipping_district_id')
    saved_ward_id = request.session.get('shipping_ward_id')
    saved_address = request.session.get('shipping_address')

    # Get locations based on saved data or user profile
    profile = request.user.profile
    selected_city = City.objects.filter(id=saved_city_id).first() if saved_city_id else profile.city
    selected_district = District.objects.filter(id=saved_district_id).first() if saved_district_id else profile.district
    selected_ward = Ward.objects.filter(id=saved_ward_id).first() if saved_ward_id else profile.ward

    # Get districts and wards based on selected locations
    districts = District.objects.filter(city=selected_city) if selected_city else []
    wards = Ward.objects.filter(district=selected_district) if selected_district else []

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': cart.get_total(),
        'total_with_shipping': cart.get_total_with_shipping(),
        'cities': City.objects.all(),  # Added cities for location selection
        'districts': districts,
        'wards': wards,
        'selected_city': selected_city,
        'selected_district': selected_district,
        'selected_ward': selected_ward,
        'saved_address': saved_address,
    }
    return render(request, 'partials/checkout/checkout-information.html', context)

@login_required
def process_checkout(request):
    if request.method == 'POST':
        try:
            cart = Cart.get_active_cart(request.user)
            if not cart:
                raise Exception("Cart not found")

            # Get the location objects
            city = City.objects.get(id=request.POST.get('city'))
            district = District.objects.get(id=request.POST.get('district'))
            ward = Ward.objects.get(id=request.POST.get('ward'))

            # Update or create shipping info
            shipping_info, created = ShippingInfo.objects.update_or_create(
                cart=cart,
                defaults={
                    'full_name': request.POST.get('full_name'),
                    'email': request.POST.get('email'),
                    'phone': request.POST.get('phone'),
                    'address': request.POST.get('address'),
                    'city': city,
                    'district': district,
                    'ward': ward,
                }
            )

            # Store in session
            request.session['shipping_info'] = {
                'full_name': shipping_info.full_name,
                'email': shipping_info.email,
                'phone': shipping_info.phone,
                'address': shipping_info.address,
                'city_id': city.id,
                'district_id': district.id,
                'ward_id': ward.id,
            }
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'redirect_url': '/checkout/shipping/'
            })
            
        except Exception as e:
            print(f"Error in process_checkout: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def shipping(request):
    cart_id = request.session.get('cart_id')
    cart = None
    
    if cart_id:
        cart = Cart.objects.filter(id=cart_id, user=request.user, is_completed=False).first()
    
    if not cart:
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if cart:
            request.session['cart_id'] = cart.id
            request.session.modified = True

    if not cart:
        messages.warning(request, 'Giỏ hàng của bạn đang trống')
        return redirect('cart:cart')

    profile = request.user.profile
    # Get shipping fee based on location hierarchy
    shipping_fee = ShippingFee.objects.filter(ward=profile.ward).first()
    if not shipping_fee:
        shipping_fee = ShippingFee.objects.filter(district=profile.district).first()
    if not shipping_fee:
        shipping_fee = ShippingFee.objects.filter(city=profile.city).first()
    
    base_shipping_fee = shipping_fee.fee if shipping_fee else 0
    express_shipping_fee = base_shipping_fee + 50000

    context = {
        'cart': cart,
        'base_shipping_fee': base_shipping_fee,
        'express_shipping_fee': express_shipping_fee,
        'total_with_shipping': cart.get_total_with_shipping()
    }
    return render(request, 'partials/checkout/checkout-shipping.html', context)

@login_required
def process_shipping(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if not cart:
            messages.error(request, 'Giỏ hàng không tồn tại')
            return redirect('cart:cart')

        profile = request.user.profile
        shipping_fee = ShippingFee.objects.filter(ward=profile.ward).first()
        if not shipping_fee:
            shipping_fee = ShippingFee.objects.filter(district=profile.district).first()
        if not shipping_fee:
            shipping_fee = ShippingFee.objects.filter(city=profile.city).first()
        
        base_shipping_fee = shipping_fee.fee if shipping_fee else 0
        shipping_method = request.POST.get('shipping_method')
        final_shipping_fee = base_shipping_fee + 50000 if shipping_method == 'express' else base_shipping_fee

        cart.shipping_method = shipping_method
        cart.shipping_fee = final_shipping_fee
        cart.save()

        return redirect('checkout:payment')
    
    return redirect('checkout:shipping')
@login_required
def payment(request):
    cart = Cart.objects.filter(user=request.user, is_completed=False).first()
    if not cart:
        messages.warning(request, 'Giỏ hàng của bạn đang trống')
        return redirect('cart:cart')
    
    if not cart.shipping_method:
        messages.warning(request, 'Vui lòng chọn phương thức vận chuyển')
        return redirect('checkout:shipping')

    context = {
        'cart': cart,
    }
    return render(request, 'partials/checkout/checkout-payment.html', context)

@login_required
def process_payment(request):
    try:
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if not cart:
            raise Exception("Giỏ hàng không tồn tại")

        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'cod':
            # Create order immediately for COD
            from orders.models import Order
            order = Order.create_from_cart(cart, payment_method)
            
            cart.is_completed = True
            cart.save()
            
            if 'cart_id' in request.session:
                del request.session['cart_id']
            request.session.modified = True
            
            messages.success(request, 'Đơn hàng của bạn đã được tạo thành công!')
            return redirect('orders:order_detail', order_id=order.id)
            
        elif payment_method == 'vnpay':
            # Store cart info in session for later order creation
            request.session['pending_payment'] = {
                'cart_id': cart.id,
                'payment_method': payment_method
            }
            request.session.modified = True
            
            # VNPAY payment processing
            vnp_Params = {}
            vnp_Params['vnp_Version'] = '2.1.0'
            vnp_Params['vnp_Command'] = 'pay'
            vnp_Params['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp_Params['vnp_Amount'] = str(int((cart.get_total() + cart.shipping_fee) * 100))
            vnp_Params['vnp_CurrCode'] = 'VND'
            vnp_Params['vnp_TxnRef'] = str(int(time.time()))
            vnp_Params['vnp_OrderInfo'] = f'Thanh toan don hang'
            vnp_Params['vnp_OrderType'] = 'billpayment'
            vnp_Params['vnp_Locale'] = 'vn'
            vnp_Params['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            vnp_Params['vnp_IpAddr'] = request.META.get('REMOTE_ADDR', '127.0.0.1')
            vnp_Params['vnp_ReturnUrl'] = request.build_absolute_uri('/checkout/vnpay-return/')

            # Sort and create hash
            sorted_params = sorted(vnp_Params.items())
            hash_data = '&'.join(f'{k}={urllib.parse.quote_plus(str(v))}' for k, v in sorted_params)
            
            vnp_SecureHash = hmac.new(
                bytes(settings.VNPAY_HASH_SECRET_KEY, 'utf-8'),
                bytes(hash_data, 'utf-8'),
                hashlib.sha512
            ).hexdigest()

            payment_url = f"{settings.VNPAY_PAYMENT_URL}?{hash_data}&vnp_SecureHash={vnp_SecureHash}"
            return redirect(payment_url)

        elif payment_method == 'momo':
            # Store cart info in session for later order creation
            request.session['pending_payment'] = {
                'cart_id': cart.id,
                'payment_method': payment_method
            }
            request.session.modified = True
            
            request_id = str(uuid.uuid4())
            
            # Prepare MoMo payment request
            momo_request_data = {
                'partnerCode': settings.MOMO_PARTNER_CODE,
                'partnerName': "DStore",
                'storeId': settings.MOMO_PARTNER_CODE,
                'requestId': request_id,
                'amount': int(cart.get_total() + cart.shipping_fee),
                'orderId': str(int(time.time())),
                'orderInfo': f'Thanh toan don hang',
                'redirectUrl': request.build_absolute_uri(reverse('checkout:momo_return')),
                'ipnUrl': request.build_absolute_uri(reverse('checkout:momo_notify')),
                'lang': 'vi',
                'requestType': 'payWithMethod',
                'orderGroupId': '',
                'autoCapture': True,
                'extraData': ''
            }
            
            # Generate signature
            raw_signature = (
                f"accessKey={settings.MOMO_ACCESS_KEY}"
                f"&amount={momo_request_data['amount']}"
                f"&extraData={momo_request_data['extraData']}"
                f"&ipnUrl={momo_request_data['ipnUrl']}"
                f"&orderId={momo_request_data['orderId']}"
                f"&orderInfo={momo_request_data['orderInfo']}"
                f"&partnerCode={momo_request_data['partnerCode']}"
                f"&redirectUrl={momo_request_data['redirectUrl']}"
                f"&requestId={momo_request_data['requestId']}"
                f"&requestType={momo_request_data['requestType']}"
            )
            
            signature = hmac.new(
                bytes(settings.MOMO_SECRET_KEY, 'utf-8'),
                bytes(raw_signature, 'utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            momo_request_data['signature'] = signature

            response = requests.post(
                settings.MOMO_API_ENDPOINT,
                data=json.dumps(momo_request_data),
                headers={
                    'Content-Type': 'application/json',
                    'Content-Length': str(len(json.dumps(momo_request_data)))
                }
            )
            data = response.json()
            
            if data.get('payUrl'):
                return redirect(data['payUrl'])
            else:
                raise Exception(data.get('message', 'Không thể tạo liên kết thanh toán MoMo'))

        else:
            raise Exception("Phương thức thanh toán không hợp lệ")
            
    except Exception as e:
        print(f"Error in process_payment: {e}")
        messages.error(request, f"Lỗi khi xử lý thanh toán: {e}")
        return redirect('checkout:payment')


    return redirect('checkout:payment')

@login_required
def vnpay_return(request):
    if request.method != 'GET':
        return HttpResponse('Invalid request method')

    input_data = request.GET
    if not input_data:
        return HttpResponse('Invalid request data')

    vnp_SecureHash = input_data.get('vnp_SecureHash')
    if not vnp_SecureHash:
        return HttpResponse('Invalid hash value')

    input_data_without_hash = dict((k, v) for k, v in input_data.items() if k != 'vnp_SecureHash')
    sorted_input_data = sorted(input_data_without_hash.items())
    hash_data = '&'.join([f'{k}={urllib.parse.quote_plus(str(v))}' for k, v in sorted_input_data])
    
    vnp_SecureHash = hmac.new(
        bytes(settings.VNPAY_HASH_SECRET_KEY, 'utf-8'),
        bytes(hash_data, 'utf-8'),
        hashlib.sha512
    ).hexdigest()

    try:
        pending_payment = request.session.get('pending_payment')
        if not pending_payment:
            return HttpResponse('Payment information not found')

        cart = Cart.objects.get(id=pending_payment['cart_id'])
        vnp_ResponseCode = input_data.get('vnp_ResponseCode')
        vnp_TransactionNo = input_data.get('vnp_TransactionNo')

        if vnp_ResponseCode == '00':
            # Create order only after successful payment
            from orders.models import Order
            order = Order.create_from_cart(cart, pending_payment['payment_method'])
            order.payment_status = 'paid'
            order.vnpay_transaction_id = vnp_TransactionNo
            order.save()
            
            cart.is_completed = True
            cart.save()
            
            if 'cart_id' in request.session:
                del request.session['cart_id']
            if 'pending_payment' in request.session:
                del request.session['pending_payment']
            request.session.modified = True
            
            messages.success(request, 'Thanh toán thành công!')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Thanh toán thất bại!')
            return redirect('checkout:payment')
            
    except Exception as e:
        messages.error(request, 'Có lỗi xảy ra trong quá trình thanh toán')
        return redirect('checkout:payment')

@login_required
def momo_return(request):
    try:
        pending_payment = request.session.get('pending_payment')
        if not pending_payment:
            return HttpResponse('Payment information not found')

        cart = Cart.objects.get(id=pending_payment['cart_id'])
        response_code = request.GET.get('resultCode')
        
        if response_code == '0':  # Success
            # Create order only after successful payment
            from orders.models import Order
            order = Order.create_from_cart(cart, pending_payment['payment_method'])
            order.payment_status = 'paid'
            order.momo_transaction_id = request.GET.get('transId')
            order.save()
            
            cart.is_completed = True
            cart.save()
            
            if 'cart_id' in request.session:
                del request.session['cart_id']
            if 'pending_payment' in request.session:
                del request.session['pending_payment']
            request.session.modified = True
            
            messages.success(request, 'Thanh toán thành công!')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Thanh toán thất bại!')
            return redirect('checkout:payment')
            
    except Exception as e:
        messages.error(request, 'Có lỗi xảy ra trong quá trình thanh toán')
        return redirect('checkout:payment')
@login_required
def order_success(request):
    # Get the most recent order for the user
    latest_order = Order.objects.filter(
        user=request.user,
    ).order_by('-created_at').first()

    if not latest_order:
        messages.error(request, 'Không tìm thấy đơn hàng')
        return redirect('cart:cart')

    context = {
        'order': latest_order,
    }
    return render(request, 'partials/checkout/order-success.html', context)


# Remove this entire function
@require_POST
def save_shipping_info(request):
    try:
        # Save all fields to session with consistent keys
        request.session['selectedFullName'] = request.POST.get('full_name')
        request.session['selectedEmail'] = request.POST.get('email')
        request.session['selectedPhone'] = request.POST.get('phone')
        request.session['selectedAddress'] = request.POST.get('address')
        request.session['selectedCity'] = request.POST.get('city')
        request.session['selectedDistrict'] = request.POST.get('district')
        request.session['selectedWard'] = request.POST.get('ward')
        request.session.modified = True
        
        # Print session data for debugging
        print("Session data saved:", {k:v for k,v in request.session.items() if 'selected' in k})
        
        return JsonResponse({'success': True})
    except Exception as e:
        print("Error saving shipping info:", str(e))
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def print_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Render the order template
        html_string = render_to_string('orders/order_print.html', {
            'order': order,
            'order_items': order.orderitem_set.all(),
        })
        
        # Create PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        
        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.order_code}.pdf"'
        html.write_pdf(response)
        
        return response
        
    except Order.DoesNotExist:
        messages.error(request, 'Không tìm thấy đơn hàng')
        return redirect('orders:order_list')


def get_districts(request, city_id):
    districts = District.objects.filter(city_id=city_id).values('id', 'name_with_type')
    return JsonResponse(list(districts), safe=False)


def get_wards(request, district_id):
    wards = Ward.objects.filter(district_id=district_id).values('id', 'name_with_type')
    return JsonResponse(list(wards), safe=False)


@require_POST
def momo_notify(request):
    try:
        # Get the notification data from MoMo
        data = json.loads(request.body)
        
        # Verify the signature
        raw_signature = f"accessKey={settings.MOMO_ACCESS_KEY}&amount={data['amount']}&extraData={data['extraData']}&orderId={data['orderId']}&orderInfo={data['orderInfo']}&orderType={data['orderType']}&partnerCode={settings.MOMO_PARTNER_CODE}&payType={data['payType']}&requestId={data['requestId']}&responseTime={data['responseTime']}&resultCode={data['resultCode']}&transId={data['transId']}"
        
        signature = hmac.new(
            bytes(settings.MOMO_SECRET_KEY, 'utf-8'),
            bytes(raw_signature, 'utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if signature != data['signature']:
            return HttpResponse(status=400)
        
        # Process the order
        order = Order.objects.get(order_code=data['orderId'])
        if data['resultCode'] == 0:  # Success
            order.payment_status = 'paid'
            order.momo_transaction_id = data['transId']
            order.save()
            
            # Mark cart as completed
            cart = Cart.objects.filter(user=order.user, is_completed=False).first()
            if cart:
                cart.is_completed = True
                cart.save()
        else:
            order.payment_status = 'failed'
            order.save()
        
        return HttpResponse(status=200)
        
    except Exception as e:
        print(f"MoMo Notify Error: {str(e)}")
        return HttpResponse(status=500)
