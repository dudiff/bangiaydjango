from django.contrib import admin
from .models import HomeSlide, InstagramPost

@admin.register(HomeSlide)
class HomeSlideAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title_start', 'title_highlighted', 'title_end', 'subtitle')

    def get_title(self, obj):
        return str(obj)
    get_title.short_description = 'Tiêu đề'


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'alt_text')
    list_filter = ('is_active', 'created_at')
    ordering = ('order',)
