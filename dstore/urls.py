"""
URL configuration for dstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from imports.views import get_product_sizes  # Update this line

urlpatterns = [
    path('admin/', admin.site.urls),
    path('imports/get-product-sizes/', get_product_sizes, name='get_product_sizes'),
    path("", include('core.urls')),
    path("user/", include("userauths.urls")),
    path('accounts/', include('allauth.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('products/', include('products.urls', namespace='products')), 
    path('shipping/', include('shipping.urls')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('promotions/', include('promotions.urls')),
    path('checkout/', include('checkout.urls')),
    path('pages/', include('pages.urls')),
    path('favorites/', include('favorites.urls', namespace='favorites')),
    path('imports/', include('imports.urls', namespace='imports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)