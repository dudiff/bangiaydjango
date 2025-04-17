from django.urls import path
from .views import DashboardView

urlpatterns = [
    path('admin/dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('dashboard-data/', DashboardView.as_view(), name='dashboard_data'),
]