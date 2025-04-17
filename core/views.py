
from django.shortcuts import render
from products.models import Brand, Product
from slider.models import HomeSlide, InstagramPost
from orders.models import OrderItem
from promotions.models import Promotion
from django.utils import timezone
import random

def index(request):
    best_sellers_data = OrderItem.get_best_sellers(limit=6)
    best_sellers = []
    
    for item in best_sellers_data:
        product = Product.objects.get(id=item['product_id'])
        if product:
            best_sellers.append({
                'product': product,
                'total_sold': item['total_sold']
            })
    
    # Get all active promotions
    all_active_promotions = Promotion.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now()
    ).order_by('?')  # Random ordering

    # Get up to 3 random promotions
    active_promotions = list(all_active_promotions)[:3]

    context = {
        'brands': Brand.objects.all().order_by('id'),
        'home_slides': HomeSlide.objects.filter(is_active=True).order_by('order'),
        'instagram_posts': InstagramPost.objects.filter(is_active=True).order_by('order'),
        'best_sellers': best_sellers,
        'active_promotions': active_promotions,
    }
    return render(request, "core/index.html", context)

