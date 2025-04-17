from django.contrib import admin
from django.urls import path
from django.db import models  
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, render
from .models import Order, OrderItem
from products.models import Product  
from django import forms

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['status'].choices = [
                ('pending', 'Đang chờ xử lý'),
                ('processing', 'Đang xử lý'),
                ('shipping', 'Đang giao hàng'),
            ]  # Chỉ cho phép 3 trạng thái này

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'product_code', 'size', 'color', 'quantity', 'price', 'total_price', 'promotions')
    can_delete = False
    extra = 0

    def product_name(self, obj):
        product = Product.objects.filter(id=obj.product_id).first()
        return f"{product.name if product else 'Sản phẩm không tồn tại'} (Size: {obj.size.name}, Màu: {obj.color.name})"
    product_name.short_description = "Tên sản phẩm"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm 
    list_display = ('order_code', 'user', 'get_created_at', 'status', 'payment_status', 'get_total_display', 'print_button')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_code', 'user__email', 'shipping_address')
    
    readonly_fields = (
        'user', 'order_code', 'payment_status', 'payment_method', 
        'shipping_fee', 'created_at', 'updated_at', 'vnpay_transaction_id'
    )

    fields = (
        'user', 'order_code', 'status', 'payment_status', 'payment_method',
        'shipping_fee', 'shipping_address', 'created_at', 'updated_at'
    )


    def get_created_at(self, obj):
        from django.utils import timezone
        local_time = timezone.localtime(obj.created_at)
        return local_time.strftime("%d/%m/%Y %H:%M:%S")
    get_created_at.admin_order_field = 'created_at'
    get_created_at.short_description = 'Ngày tạo'

    def print_button(self, obj):
        return format_html('<a class="button" href="{}?order_id={}" target="_blank">In hóa đơn</a>', 'print/', obj.id)
    print_button.short_description = 'In hóa đơn'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print/', self.admin_site.admin_view(self.print_order_view), name='order_print'),
        ]
        return custom_urls + urls

    def print_order_view(self, request):
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        items = []
        for item in order.order_items.all():
            product = Product.objects.filter(id=item.product_id).first()
            item.product_name = product.name if product else "Sản phẩm không tồn tại"
            items.append(item)
        return render(request, 'admin/orders/order_print.html', {'order': order, 'order_items': items})

    def get_total_display(self, obj):
        total_with_shipping = obj.total_amount + obj.shipping_fee
        return f"{total_with_shipping:,.0f} VNĐ"  # Hiển thị có dấu phân cách
    get_total_display.short_description = 'Tổng tiền'
    get_total_display.admin_order_field = 'total_amount'
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            if old_obj.status in ['delivered', 'cancelled']:
                return  # Không cho phép chỉnh sửa đơn đã giao hoặc hủy

            if not request.user.is_superuser:
                allowed_statuses = ['pending', 'processing', 'shipping']
                if obj.status not in allowed_statuses:
                    obj.status = old_obj.status

            if obj.status == 'delivered':
                obj.payment_status = 'paid'

            total_items_price = sum(item.total_price for item in obj.order_items.all())
            obj.total_amount = total_items_price + (obj.shipping_fee or 0)  # Nếu phí ship None thì mặc định là 0

        if not obj.order_code:
            last_order = Order.objects.order_by('-id').first()
            obj.order_code = f"{int(last_order.order_code) + 1:04d}" if last_order and last_order.order_code.isdigit() else "0001"

        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False  # Không cho phép thêm đơn hàng từ Admin

    def has_change_permission(self, request, obj=None):
        return False if obj and obj.status == 'delivered' else super().has_change_permission(request, obj)