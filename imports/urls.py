from django.urls import path
from . import views

app_name = 'imports'

urlpatterns = [
    path('', views.import_order_list, name='import_order_list'),
    path('create/', views.import_order_create, name='import_order_create'),
    path('<int:order_id>/', views.import_order_detail, name='import_order_detail'),
    path('get-product-sizes/', views.get_product_sizes, name='get_product_sizes'),
    path('get-supplier-products/', views.get_supplier_products, name='get_supplier_products'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('print-order/<int:order_id>/', views.print_order, name='print_order'),
    path('print-order-list/', views.print_order_list, name='print_order_list'),
]