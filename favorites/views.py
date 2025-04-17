from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import FavoriteItem
from products.models import Product

@login_required
@csrf_protect
def toggle_favorite(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            favorite = FavoriteItem.objects.filter(
                user=request.user,
                product=product
            ).first()
            
            message = ''
            if favorite:
                # Remove from favorites
                favorite.delete()
                is_favorite = False
                message = 'Đã xóa khỏi danh sách yêu thích'
            else:
                # Add to favorites
                FavoriteItem.objects.create(
                    user=request.user,
                    product=product
                )
                is_favorite = True
                message = 'Đã thêm vào danh sách yêu thích'
                
            return JsonResponse({
                'status': 'success',
                'is_favorite': is_favorite,
                'message': message,
                'product_id': product_id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': 'Có lỗi xảy ra, vui lòng thử lại'
            }, status=500)
    return JsonResponse({
        'status': 'error', 
        'message': 'Yêu cầu không hợp lệ'
    }, status=400)

@login_required
def favorite_list(request):
    favorites = FavoriteItem.objects.filter(user=request.user)
    return render(request, 'favorites/favorite_list.html', {
        'favorites': favorites
    })
