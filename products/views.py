from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Product, 
    Category, 
    Review, 
    ProductSizeInventory  # Add this import
)
from favorites.models import FavoriteItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order, OrderItem  # Import OrderItem
from django.db.models import Count, Avg
from .models import Product, Brand, Size, UsePurpose, ShoeType, Material, ColorType
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.expressions import RawSQL
import random
from django.http import JsonResponse
from .models import Product

def all_men_products(request):
    products = Product.objects.filter(category__name__iexact='Nam')
    # Get filters
    purpose_id = request.GET.get('purpose')
    shoe_type_id = request.GET.get('shoe_type')
    material_id = request.GET.get('material')
    label = request.GET.get('label')
    # Apply filters
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)
    else:
        purpose = None

    if shoe_type_id:
        shoe_type = ShoeType.objects.get(id=shoe_type_id)
        products = products.filter(shoe_type=shoe_type)
    else:
        shoe_type = None

    if material_id:
        material = Material.objects.get(id=material_id)
        products = products.filter(material=material)
    else:
        material = None

    if label:
        products = products.filter(labels=label)

    # Handle label filter
    label = request.GET.get('label')
    if label:
        products = products.filter(labels=label)
    favorite_products = []
    if request.user.is_authenticated:
        favorite_products = Product.objects.filter(
            favoriteitem__user=request.user
        )
    # Handle material filter
    material_id = request.GET.get('material')
    if material_id:
        products = products.filter(material_id=material_id)
    
    # Handle shoe type filter
    shoe_type_id = request.GET.get('shoe_type')
    if shoe_type_id:
        products = products.filter(shoe_type_id=shoe_type_id)

    # Get purpose filter
    purpose_id = request.GET.get('purpose')
    purpose = None
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)

    purposes = UsePurpose.objects.filter(
        purpose_types__regex=r'(^1$|^1,|,1$|,1,)'  # Exact match for '1' (men's category)
    ).exclude(
        purpose_types__regex=r'[0-9][0-9]'  # Exclude cases where '1' is part of a larger number
    ).distinct()
    
    brands = Brand.objects.filter(
        brand_types__contains='1',  # Only brands for men
        product__category__name__iexact='Nam'
    ).annotate(
        product_count=Count('product', filter=Q(product__category__name__iexact='Nam'))
    ).distinct()

    # Get random brands for menu display menu_brands = brands.order_by('?')[:4]
    

    # Get sizes with product count
    sizes = Size.objects.filter(product__category__name__iexact='Nam')\
        .annotate(product_count=Count('product'))\
        .distinct()
    colors = ColorType.objects.filter(product__category__name__iexact='Nam')\
        .annotate(product_count=Count('product'))\
        .distinct()
    color_ids = request.GET.getlist('colors')
    if color_ids:
        products = products.filter(colors__id__in=color_ids)
    # Handle price filter
    min_price = request.GET.get('price_min')
    max_price = request.GET.get('price_max')
    
    # Chuyển đổi giá trị và lọc sản phẩm theo khoảng giá
    if min_price and min_price.replace(',', '').isdigit():
        min_price = int(min_price.replace(',', ''))
        products = products.filter(price__gte=min_price)
    if max_price and max_price.replace(',', '').isdigit():
        max_price = int(max_price.replace(',', ''))
        products = products.filter(price__lte=max_price)

    # Handle brand filter
    brand_ids = request.GET.getlist('brands')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)

    # Handle size filter
    size_ids = request.GET.getlist('sizes')
    if size_ids:
        products = products.filter(sizes__id__in=size_ids)

    # Handle sorting
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
    # Lấy offset để xác định số sản phẩm cần hiển thị
    total_products = products.count()
    offset = int(request.GET.get('offset', 0))
    limit = 9
    products_page = products[offset:offset + limit]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('partials/product/men/product_items.html', {
            'products': products_page,
            'favorite_products': favorite_products,
            'request': request,
        })
        return JsonResponse({
            'html': html,
            'has_next': offset + limit < total_products,
            'next_offset': offset + limit,
            'shown_products': offset + len(products_page),
            'total_products': total_products
        })
    context = {
        'products': products_page,  # Change this line to use paginated products
        'total_products': products.count(),  # Add total count
        'material': material,
        'shoe_type': shoe_type,
        'purpose': purpose,
        'label': label,
         #'menu_brands': menu_brands, 
        'brands': brands,
        'sizes': sizes,
        'colors': colors,
        'selected_colors': color_ids,
        'purposes': purposes,  # Add this line
        'selected_brands': brand_ids,
        'selected_sizes': size_ids,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'product_count': products.count(),
        'favorite_products': favorite_products,
    }
    return render(request, 'partials/product/men/allmen.html', context)

def all_women_products(request):
    products = Product.objects.filter(category__name__iexact='Nữ')
    # Get filters
    purpose_id = request.GET.get('purpose')
    shoe_type_id = request.GET.get('shoe_type')
    material_id = request.GET.get('material')
    label = request.GET.get('label')
    # Apply filters
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)
    else:
        purpose = None

    if shoe_type_id:
        shoe_type = ShoeType.objects.get(id=shoe_type_id)
        products = products.filter(shoe_type=shoe_type)
    else:
        shoe_type = None

    if material_id:
        material = Material.objects.get(id=material_id)
        products = products.filter(material=material)
    else:
        material = None

    if label:
        products = products.filter(labels=label)

    # Handle label filter
    label = request.GET.get('label')
    if label:
        products = products.filter(labels=label)
    favorite_products = []
    if request.user.is_authenticated:
        favorite_products = Product.objects.filter(
            favoriteitem__user=request.user
        )
    # Handle material filter
    material_id = request.GET.get('material')
    if material_id:
        products = products.filter(material_id=material_id)
    
    # Handle shoe type filter
    shoe_type_id = request.GET.get('shoe_type')
    if shoe_type_id:
        products = products.filter(shoe_type_id=shoe_type_id)

    # Get purpose filter
    purpose_id = request.GET.get('purpose')
    purpose = None
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)

    # Update brands query with regex pattern
    brands = Brand.objects.filter(
        brand_types__regex=r'(^2$|^2,|,2$|,2,)',  # Exact match for '2' (women's category)
        product__category__name__iexact='Nữ'
    ).annotate(
        product_count=Count('product', filter=Q(product__category__name__iexact='Nữ'))
    ).exclude(
        brand_types__regex=r'[0-9][0-9]'  # Exclude cases where '2' is part of a larger number
    ).distinct()

    # Update purposes query with regex pattern
    purposes = UsePurpose.objects.filter(
        purpose_types__regex=r'(^2$|^2,|,2$|,2,)'  # Exact match for '2' (women's category)
    ).exclude(
        purpose_types__regex=r'[0-9][0-9]'  # Exclude cases where '2' is part of a larger number
    ).distinct()

    # Fix colors query to show women's products colors instead of men's
    colors = ColorType.objects.filter(
        product__category__name__iexact='Nữ'
    ).annotate(
        product_count=Count('product')
    ).distinct()

    # Get sizes with product count
    sizes = Size.objects.filter(product__category__name__iexact='Nữ')\
        .annotate(product_count=Count('product'))\
        .distinct()
    # Handle price filter
    min_price = request.GET.get('price_min')
    max_price = request.GET.get('price_max')
    color_ids = request.GET.getlist('colors')
    if color_ids:
        products = products.filter(colors__id__in=color_ids)
    # Chuyển đổi giá trị và lọc sản phẩm theo khoảng giá
    if min_price and min_price.replace(',', '').isdigit():
        min_price = int(min_price.replace(',', ''))
        products = products.filter(price__gte=min_price)
    if max_price and max_price.replace(',', '').isdigit():
        max_price = int(max_price.replace(',', ''))
        products = products.filter(price__lte=max_price)

    # Handle brand filter
    brand_ids = request.GET.getlist('brands')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)

    # Handle size filter
    size_ids = request.GET.getlist('sizes')
    if size_ids:
        products = products.filter(sizes__id__in=size_ids)

    # Handle sorting
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
    total_products = products.count()

    # Lấy offset để xác định số sản phẩm cần hiển thị
    offset = int(request.GET.get('offset', 0))
    limit = 9
    products_page = products[offset:offset + limit]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('partials/product/women/product_items.html', {
            'products': products_page,
            'favorite_products': favorite_products,
            'request': request,
        })
        return JsonResponse({
            'html': html,
            'has_next': offset + limit < total_products,
            'next_offset': offset + limit,
            'shown_products': offset + len(products_page),
            'total_products': total_products
        })
    context = {
        'products': products_page,  # Change this to use paginated products
        'total_products': products.count(),
        'material': material,  # Add this
        'shoe_type': shoe_type,  # Add this
        'purpose': purpose,  # Add this
        'label': label,
        'brands': brands,
        'sizes': sizes,
        'colors': colors,
        'selected_colors': color_ids,
        'purposes': purposes,  # Add this line
        'selected_brands': brand_ids,
        'selected_sizes': size_ids,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'product_count': products.count(),
        'favorite_products': favorite_products,
    }
    return render(request, 'partials/product/women/allwomen.html', context)

def all_kids_products(request):
    products = Product.objects.filter(category__name__iexact='Trẻ em')
    # Get filters
    purpose_id = request.GET.get('purpose')
    shoe_type_id = request.GET.get('shoe_type')
    material_id = request.GET.get('material')
    label = request.GET.get('label')
    # Apply filters
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)
    else:
        purpose = None

    if shoe_type_id:
        shoe_type = ShoeType.objects.get(id=shoe_type_id)
        products = products.filter(shoe_type=shoe_type)
    else:
        shoe_type = None

    if material_id:
        material = Material.objects.get(id=material_id)
        products = products.filter(material=material)
    else:
        material = None

    if label:
        products = products.filter(labels=label)
    favorite_products = []
    if request.user.is_authenticated:
        favorite_products = Product.objects.filter(
            favoriteitem__user=request.user
        )
    # Handle label filter
    label = request.GET.get('label')
    if label:
        products = products.filter(labels=label)
    
    # Handle material filter
    material_id = request.GET.get('material')
    if material_id:
        products = products.filter(material_id=material_id)
    colors = ColorType.objects.filter(product__category__name__iexact='Trẻ em')\
        .annotate(product_count=Count('product'))\
        .distinct()
    # Handle shoe type filter
    shoe_type_id = request.GET.get('shoe_type')
    if shoe_type_id:
        products = products.filter(shoe_type_id=shoe_type_id)

    # Get purpose filter
    purpose_id = request.GET.get('purpose')
    purpose = None
    if purpose_id:
        purpose = UsePurpose.objects.get(id=purpose_id)
        products = products.filter(use_purpose=purpose)

    # Get use purposes
    purposes = UsePurpose.objects.all()
    
    brands = Brand.objects.annotate(
        has_kids=RawSQL("FIND_IN_SET(%s, brand_types)", ('3',))
    ).filter(has_kids__gt=0, product__category__name__iexact='Trẻ em').annotate(
        product_count=Count('product')
    ).distinct()

    # Get sizes with product count
    sizes = Size.objects.filter(product__category__name__iexact='Trẻ em')\
        .annotate(product_count=Count('product'))\
        .distinct()
    color_ids = request.GET.getlist('colors')
    if color_ids:
        products = products.filter(colors__id__in=color_ids)
    # Handle price filter
    min_price = request.GET.get('price_min')
    max_price = request.GET.get('price_max')
    
    # Chuyển đổi giá trị và lọc sản phẩm theo khoảng giá
    if min_price and min_price.replace(',', '').isdigit():
        min_price = int(min_price.replace(',', ''))
        products = products.filter(price__gte=min_price)
    if max_price and max_price.replace(',', '').isdigit():
        max_price = int(max_price.replace(',', ''))
        products = products.filter(price__lte=max_price)

    # Handle brand filter
    brand_ids = request.GET.getlist('menu_brands')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)

    # Handle size filter
    size_ids = request.GET.getlist('sizes')
    if size_ids:
        products = products.filter(sizes__id__in=size_ids)

    # Handle sorting
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
    # Add pagination
    total_products = products.count()
    # Lấy offset để xác định số sản phẩm cần hiển thị
    offset = int(request.GET.get('offset', 0))
    limit = 9
    products_page = products[offset:offset + limit]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('partials/product/kids/product_items.html', {
            'products': products_page,
            'favorite_products': favorite_products,
            'request': request,
        })
        return JsonResponse({
            'html': html,
            'has_next': offset + limit < total_products,
            'next_offset': offset + limit,
            'shown_products': offset + len(products_page),
            'total_products': total_products
        })
    context = {
        'products': products_page,  # Change this to use paginated products
        'total_products': products.count(),
        'material': material,  # Add this
        'shoe_type': shoe_type,  # Add this
        'purpose': purpose,  # Add this
        'label': label,
         #'menu_brands': menu_brands,
        'brands': brands,
        'sizes': sizes,
        'colors': colors,
        'selected_colors': color_ids,
        'purposes': purposes,  # Add this line
        'selected_brands': brand_ids,
        'selected_sizes': size_ids,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'total_products': products.count(), 
        'favorite_products': favorite_products,
    }
    return render(request, 'partials/product/kids/allkids.html', context)

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().select_related('user')
    images = product.images.all()
    
    # Check if product is in user's favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteItem.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    # Get available sizes with inventory
    sizes_with_inventory = []
    for size in product.sizes.all():
        try:
            inventory = ProductSizeInventory.objects.get(product=product, size=size)
            sizes_with_inventory.append({
                'size': size,
                'quantity': inventory.quantity,
                'available': inventory.quantity > 0
            })
        except ProductSizeInventory.DoesNotExist:
            sizes_with_inventory.append({
                'size': size,
                'quantity': 0,
                'available': False
            })

    # Updated related products query
    related_products = Product.objects.filter(
        category=product.category  # Must be same category
    ).filter(
        Q(brand=product.brand, use_purpose=product.use_purpose) |  # Same brand AND purpose
        Q(brand=product.brand, shoe_type=product.shoe_type) |      # Same brand AND shoe type
        Q(use_purpose=product.use_purpose, shoe_type=product.shoe_type)  # Same purpose AND shoe type
    ).exclude(
        id=product.id
    ).distinct()

    # If we don't have enough products, fallback to simpler criteria but still same category
    if related_products.count() < 4:
        related_products = Product.objects.filter(
            category=product.category
        ).filter(
            Q(brand=product.brand) |
            Q(use_purpose=product.use_purpose)
        ).exclude(
            id=product.id
        ).distinct()

    related_products = related_products.order_by('?')[:4]

    has_purchased = False
    has_reviewed = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product_id=product.id,
            order__status='completed'
        ).exists()
        has_reviewed = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    # Calculate review statistics with percentages
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Create review summary - FIX: Use dictionary with string keys for ratings
    review_summary = {}
    if total_reviews > 0:
        for rating in range(1, 6):  # Changed to start from 1 to 5
            count = reviews.filter(rating=rating).count()
            percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
            review_summary[str(rating)] = {
                'count': count,
                'percentage': percentage
            }
    
    context = {
        'product': product,
        'reviews': reviews,
        'images': images,
        'review_summary': review_summary,
        'has_purchased': has_purchased,
        'has_reviewed': has_reviewed,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'related_products': related_products,
        'sizes_with_inventory': sizes_with_inventory,
        'is_favorite': is_favorite,
    }
    return render(request, 'core/product.html', context)
@login_required
def add_review(request, product_id):
    if request.method != "POST":
        return redirect('products:product_detail', product_id=product_id)

    product = get_object_or_404(Product, id=product_id)
    
    # Kiểm tra đã mua hàng chưa
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product_id=product.id,
        order__status='completed'
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'Bạn cần mua sản phẩm này trước khi đánh giá.')
        return redirect('products:product_detail', product_id=product_id)

    # Kiểm tra đã review chưa
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, 'Bạn đã đánh giá sản phẩm này rồi.')
        return redirect('products:product_detail', product_id=product_id)

    try:
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        
        if not (1 <= rating <= 5 and comment):
            raise ValueError('Invalid rating or comment')

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')
        
    except (ValueError, TypeError):
        messages.error(request, 'Vui lòng điền đầy đủ đánh giá và nhận xét.')
    
    return redirect('products:product_detail', product_id=product_id)
def brand_products(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    products = Product.objects.filter(brand=brand)
    
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'partials/product/brands/brand_products.html', context)

def all_brands(request):
    brands = Brand.objects.all()
    return render(request, 'partials/product/brands/all_brands.html', {'brands': brands})
def all_products(request):
    # Get search parameters
    category_filter = request.GET.get('category')
    brand_filter = request.GET.get('brand')
    search_query = request.GET.get('search')
    label_filter = request.GET.get('label')

    # Base queryset
    products = Product.objects.all()

    # Apply filters
    if category_filter:
        products = products.filter(category__name__iexact=category_filter)
    
    if brand_filter:
        products = products.filter(brand__id=brand_filter)
    
    if search_query:
        products = products.filter(name__icontains=search_query)

    if label_filter:  # Add this block
        products = products.filter(labels=label_filter)

    favorite_products = []
    if request.user.is_authenticated:
        favorite_products = Product.objects.filter(
            favoriteitem__user=request.user
        )
    # Get categories and brands for filters
    categories = Category.objects.all()
    brands = Brand.objects.annotate(product_count=Count('product'))

    # Group products by category
    products_by_category = {}
    for category in categories:
        products_by_category[category] = products.filter(category=category)

    # Get price filters
    min_price = request.GET.get('price_min', '').replace('.', '')  # Remove dots from formatted number
    max_price = request.GET.get('price_max', '').replace('.', '')

    # Apply price filters
    if min_price.isdigit():
        products_by_category = {
            category: [p for p in prods if (p.sale_price or p.price) >= int(min_price)]
            for category, prods in products_by_category.items()
        }

    if max_price.isdigit():
        products_by_category = {
            category: [p for p in prods if (p.sale_price or p.price) <= int(max_price)]
            for category, prods in products_by_category.items()
        }

    context = {
        'products_by_category': products_by_category,
        'categories': categories,
        'brands': brands,
        'selected_category': category_filter,
        'selected_brand': brand_filter,
        'selected_label': label_filter,
        'search_query': search_query if search_query else "", 
        'total_products': products.count(),
        'favorite_products': favorite_products,
    }
    return render(request, 'partials/product/allproduct.html', context)
# def some_view_function(request):
#     # Retrieve the cart object for the user
#     cart = Cart.objects.get(user=request.user, is_completed=False)  # Example of retrieving the cart

#     # Define payment_method and request as needed
#     payment_method = 'cod'  # Example payment method

#     # Example usage in a view or function
#     order = OrderItem.create_from_cart(cart, payment_method, request)

def get_product_sizes(request):
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            sizes = [{'id': size.id, 'name': size.name} for size in product.sizes.all()]
            return JsonResponse({'sizes': sizes})
        except Product.DoesNotExist:
            pass
    return JsonResponse({'sizes': []})