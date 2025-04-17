from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('allmen/', views.all_men_products, name='allmen'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('men/', views.all_men_products, name='allmen'),
    path('women/', views.all_women_products, name='allwomen'),
    path('kids/', views.all_kids_products, name='allkids'),
    path('brands/', views.all_brands, name='all_brands'),
    path('brands/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('all-products/', views.all_products, name='all_products'),
]
