from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('apply/', views.apply_promotion, name='apply'),
    path('remove/', views.remove_promotion, name='remove'),
]