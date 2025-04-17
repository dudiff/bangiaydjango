from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    path('list/', views.favorite_list, name='favorite-list'),
]