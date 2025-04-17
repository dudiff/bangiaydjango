from django.contrib import admin
from .models import AboutUs, ShoeGuide, Contact

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(ShoeGuide)
class ShoeGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    readonly_fields = ('first_name', 'last_name', 'email', 'subject', 'message', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Họ và tên"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Mark as read when viewing
        obj = self.get_object(request, object_id)
        if obj and not obj.is_read:
            obj.is_read = True
            obj.save()
        return super().change_view(request, object_id, form_url, extra_context)
