from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('api/cities/', views.get_cities, name='get_cities'),
    path('api/districts/<int:city_id>/', views.get_districts, name='get_districts'),
    path('api/wards/<int:district_id>/', views.get_wards, name='get_wards'),
    path('api/shipping-fee/<int:city_id>/', views.get_shipping_fee, name='get_shipping_fee'),
    path('api/shipping-fee/<int:city_id>/<int:district_id>/', views.get_shipping_fee, name='get_shipping_fee_district'),
    path('api/shipping-fee/<int:city_id>/<int:district_id>/<int:ward_id>/', views.get_shipping_fee, name='get_shipping_fee_ward'),
]