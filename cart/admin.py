from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):  
    model = CartItem  
    extra = 0  # Không hiển thị thêm dòng trống
    can_delete = False  # Không cho phép xóa CartItem  
    readonly_fields = ('product', 'size', 'color', 'quantity')  # Chỉ đọc các trường này  

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_completed')  
    list_filter = ('is_completed',) 
    search_fields = ('user__username',)  
    readonly_fields = ('user', 'created_at', 'is_completed')  

    inlines = [CartItemInline]  # Hiển thị CartItem trong trang Cart  

    def has_add_permission(self, request):
        """Không cho phép admin thêm giỏ hàng mới"""
        return False  

    def has_change_permission(self, request, obj=None):
        """Không cho phép admin chỉnh sửa giỏ hàng"""
        return False  

    def has_delete_permission(self, request, obj=None):
        """Không cho phép admin xóa giỏ hàng"""
        return False  

admin.site.register(Cart, CartAdmin)
