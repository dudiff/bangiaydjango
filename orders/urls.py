from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('print/<int:order_id>/', views.print_order, name='print_order'),
    path('<int:order_id>/confirm-delivery/', views.confirm_delivery, name='confirm-delivery'),
    path('<int:order_id>/confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]