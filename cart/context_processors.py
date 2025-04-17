from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        cart = Cart.get_active_cart(request.user)
        return {
            'cart': cart,
            'cart_items': cart.items.all() if cart else [],
            'cart_total': cart.get_total() if cart else 0,
        }
    return {
        'cart': None,
        'cart_items': [],
        'cart_total': 0,
    }
