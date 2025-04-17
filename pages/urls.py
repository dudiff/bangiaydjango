from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about_view, name='about'),
    path('shoe-guide/', views.shoe_guide_view, name='shoe_guide'),
    path('contact/', views.contact_view, name='contact'),
]