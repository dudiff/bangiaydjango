from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/dropdown/', views.cart_dropdown, name='cart_dropdown'),
    path('remove-item/<int:item_id>/', views.remove_item, name='remove_item'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('update-color/<int:item_id>/', views.update_color, name='update_color'),  # Add this line
]
