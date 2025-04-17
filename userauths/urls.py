from django.urls import path
from userauths import views
from .views import activate_account
from shipping.views import get_districts, get_wards 

app_name = "userauths"

urlpatterns = [
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate'),
    path('activation-email/', views.activation_email_view, name='activation_email'),
    path('profile/', views.profile_view, name='profile'),  
    path('profile/edit/', views.edit_profile_view, name='edit_profile'), 
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
]