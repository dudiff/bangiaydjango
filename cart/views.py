from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from products.models import Product, Size, ColorType
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        size_name = request.POST.get("size")
        color_name = request.POST.get("color")

        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(Size, name=size_name)
        color = get_object_or_404(ColorType, name=color_name)

        # Get or create single cart
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if not cart:
            cart = Cart.objects.create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        request.session['cart_id'] = cart.id
        request.session.modified = True

        messages.success(request, f"Sản phẩm {product.name} đã được thêm vào giỏ hàng.")
        return redirect('products:product_detail', product_id=product.id)

@login_required
def cart_view(request):
    # Get all incomplete carts for the user
    carts = Cart.objects.filter(user=request.user, is_completed=False)
    
    if carts.count() > 1:
        # Keep the latest cart and delete others
        latest_cart = carts.order_by('-created_at').first()
        carts.exclude(id=latest_cart.id).delete()
        cart = latest_cart
    else:
        cart = carts.first()

    if not cart:
        cart = Cart.objects.create(user=request.user)

    # Update session with current cart
    request.session['cart_id'] = cart.id
    request.session.modified = True

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'core/cart.html', context)

def index_view(request):
    return render(request, 'core/index.html')  

def cart_dropdown(request):
    if request.user.is_authenticated:
        # Get the active cart from session or database
        cart = Cart.objects.filter(user=request.user, is_completed=False).first()
        if cart:
            cart_items = cart.items.all()
            grand_total = sum(item.product.price * item.quantity for item in cart_items)
        else:
            cart_items = []
            grand_total = 0
    else:
        cart_items = []
        grand_total = 0

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'partials/cart/cart-dropdown.html', context)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, f"Sản phẩm {cart_item.product.name} đã được xóa khỏi giỏ hàng.")
    return redirect('cart:cart')

@login_required
def remove_item(request, item_id):
    cart = Cart.objects.filter(user=request.user, is_completed=False).first()
    if cart:
        cart.remove_item(item_id)
        
        # Check if cart is empty after removal
        if cart.items.count() == 0:
            # Remove promotion if cart is empty
            if cart.promotion:
                cart.promotion = None
                cart.save()
                messages.info(request, "Mã giảm giá đã bị xóa do giỏ hàng trống.")
            messages.success(request, "Sản phẩm đã được xóa khỏi giỏ hàng.")
        else:
            messages.success(request, "Sản phẩm đã được xóa khỏi giỏ hàng.")
    else:
        messages.error(request, "Không tìm thấy sản phẩm trong giỏ hàng.")

    return redirect('cart:cart')
@login_required
def update_quantity(request, item_id):
    cart = Cart.objects.filter(user=request.user, is_completed=False).first()
    quantity = request.POST.get('quantity')

    # Validate and convert quantity to an integer
    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
    except (ValueError, TypeError):
        messages.error(request, 'Invalid quantity provided.')
        return redirect('cart:cart')

    if cart:
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()

        # Update the total price of the cart
        cart_total = sum(item.product.price * item.quantity for item in cart.items.all())
        cart.total_price = cart_total
        cart.save()

        messages.success(request, 'Quantity updated successfully.')
    else:
        messages.error(request, 'Cart not found.')

    return redirect('cart:cart')

@login_required
def update_color(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    color_name = request.POST.get('color')
    color = get_object_or_404(ColorType, name=color_name)
    cart_item.color = color
    cart_item.save()
    return redirect('cart:cart')
