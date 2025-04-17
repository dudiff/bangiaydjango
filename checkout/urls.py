from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('information/', views.checkout_information, name='information'),
    path('process/', views.process_checkout, name='process_checkout'),
    path('shipping/', views.shipping, name='shipping'),
    path('process-shipping/', views.process_shipping, name='process_shipping'),
    path('payment/', views.payment, name='payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('vnpay-return/', views.vnpay_return, name='vnpay_return'),
    path('momo-return/', views.momo_return, name='momo_return'),  # Changed from momo-return to momo_return
    path('momo-notify/', views.momo_notify, name='momo_notify'),  # Changed from momo-notify to momo_notify
    path('order-success/', views.order_success, name='order_success'),
    path('save-shipping-info/', views.save_shipping_info, name='save_shipping_info'),
    path('print-order/<int:order_id>/', views.print_order, name='print_order'),
    path('api/districts/<int:city_id>/', views.get_districts, name='get_districts'),
    path('api/wards/<int:district_id>/', views.get_wards, name='get_wards'),
]