from django.contrib import admin
from django.utils import timezone
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    def is_currently_valid(self, obj):
        now = timezone.now()
        is_valid = obj.is_active and obj.valid_from <= now <= obj.valid_to
        return is_valid
    is_currently_valid.boolean = True
    is_currently_valid.short_description = 'Hiệu lực'
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 
                   'valid_to', 'is_currently_valid', 'usage_limit', 'times_used')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
    readonly_fields = ('times_used', 'created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'description', 'is_active', 'image')
        }),
        ('Giảm giá', {
            'fields': ('discount_type', 'discount_value', 'min_purchase', 'max_discount')
        }),
        ('Thời gian hiệu lực', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Giới hạn sử dụng', {
            'fields': ('usage_limit', 'times_used')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )