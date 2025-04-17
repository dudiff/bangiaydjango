from django.contrib import admin
from django.urls import path
from . import views
from django.db import models

# Create a dummy model for dashboard
class Dashboard(models.Model):
    class Meta:
        verbose_name_plural = "Dashboard"
        app_label = "dashboard"

    def __str__(self):
        return "Dashboard"

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', views.DashboardView.as_view(), name='dashboard-view'),
        ]
        return custom_urls + urls

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
