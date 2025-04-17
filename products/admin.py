from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Brand, Product, ShoeType, Material, UsePurpose, 
                    ColorType, Size, ProductImage, Review, Supplier, ProductSizeInventory)
from django.contrib import messages
from django.utils.safestring import mark_safe
# Add ProductSizeInventory inline for Product
class ProductSizeInventoryInline(admin.TabularInline):
    model = ProductSizeInventory
    extra = 1
    readonly_fields = ['quantity']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "size":
            # Get the parent Product instance
            parent_instance = self.get_parent_object(request)
            if parent_instance:
                # Only show sizes that are linked to this product through M2M
                kwargs["queryset"] = parent_instance.sizes.all()
            else:
                kwargs["queryset"] = Size.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_parent_object(self, request):
        if not hasattr(self, 'parent_instance'):
            if request.resolver_match.kwargs.get('object_id'):
                self.parent_instance = Product.objects.get(pk=request.resolver_match.kwargs['object_id'])
            else:
                self.parent_instance = None
        return self.parent_instance

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInventoryInline]
    list_display = ('name', 'price', 'sale_price', 'purchase_price', 'category', 'brand', 'stock', 'image_display', 'labels_display', 'get_supplier_name')
    readonly_fields = ('product_code',)
    list_filter = ('category', 'brand', 'labels', 'supplier') 
    search_fields = ('name', 'product_code', 'description', 'category__name', 'brand__name', 'supplier__name')
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Get the product instance
        product = form.instance
        
        # Create inventory records for all sizes
        for size in product.sizes.all():
            ProductSizeInventory.objects.get_or_create(
                product=product,
                size=size,
                defaults={'quantity': 0}
            )
        
        # Remove inventory records for sizes that were removed
        ProductSizeInventory.objects.filter(
            product=product
        ).exclude(
            size__in=product.sizes.all()
        ).delete()
    actions = ['mark_as_sale', 'mark_as_hot', 'mark_as_new', 'clear_labels']

    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50px" height="50px" />', obj.image.url)
        return "No Image"
    
    image_display.allow_tags = True
    image_display.short_description = 'Ảnh'

    def labels_display(self, obj):
        return ", ".join(obj.labels) if obj.labels else "Không có nhãn"
    
    labels_display.short_description = "Nhãn"
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else "No Supplier" 
    
    get_supplier_name.short_description = "Nhà Cung Cấp" 
    
    @admin.action(description="Đánh dấu là SALE")
    def mark_as_sale(self, request, queryset):
        queryset.update(labels=['Sale'])

    @admin.action(description="Đánh dấu là HOT")
    def mark_as_hot(self, request, queryset):
        queryset.update(labels=['Hot'])

    @admin.action(description="Đánh dấu là NEW")
    def mark_as_new(self, request, queryset):
        queryset.update(labels=['New'])

    @admin.action(description="Xóa tất cả nhãn")
    def clear_labels(self, request, queryset):
        queryset.update(labels=[])
    def changelist_view(self, request, extra_context=None):
        # Check low stock products
        low_stock_products = Product.objects.filter(stock__lt=10)
        low_stock_sizes = ProductSizeInventory.objects.filter(quantity__lt=10)
        
        # Prepare messages
        if low_stock_products.exists() or low_stock_sizes.exists():
            warning_messages = []
            for product in low_stock_products:
                warning_messages.append(f"Sản phẩm '{product.name}' còn {product.stock} trong kho!")
            
            for inventory in low_stock_sizes:
                warning_messages.append(f"Size {inventory.size.name} của '{inventory.product.name}' chỉ còn {inventory.quantity}!")
            
            self.message_user(request, mark_safe("<br>".join(warning_messages)), messages.WARNING)
        
        return super().changelist_view(request, extra_context)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'comment', 'created_at')  # Hiển thị danh sách
    readonly_fields = ('user', 'product', 'rating', 'comment', 'created_at')  # Không cho sửa

    def has_add_permission(self, request):
        return False  # Chặn quyền thêm

    def has_change_permission(self, request, obj=None):
        return False  # Chặn quyền sửa

    def has_delete_permission(self, request, obj=None):
        return False  # Chặn quyền xóa

@admin.register(ProductSizeInventory)
class ProductSizeInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'quantity']
    list_filter = ['product', 'size']
    search_fields = ['product__name', 'size__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "size":
            if request.GET.get('product'):
                product_id = request.GET.get('product')
                try:
                    product = Product.objects.get(id=product_id)
                    kwargs["queryset"] = product.sizes.all()
                except Product.DoesNotExist:
                    kwargs["queryset"] = Size.objects.none()
            elif getattr(self, 'instance', None) and self.instance.product:
                kwargs["queryset"] = self.instance.product.sizes.all()
            else:
                kwargs["queryset"] = Size.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.product:
            # Get sizes from ProductSizeInventory relationship
            form.base_fields['size'].queryset = Size.objects.filter(
                productsizeinventory__product=obj.product
            ).distinct()
        else:
            form.base_fields['size'].queryset = Size.objects.none()
        return form

admin.site.register(Review, ReviewAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ShoeType)
admin.site.register(Material)
admin.site.register(UsePurpose)
admin.site.register(ColorType)
admin.site.register(Size)
admin.site.register(ProductImage)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'get_brands']
    list_filter = ['brands']
    search_fields = ['name', 'email', 'phone']

    def get_brands(self, obj):
        return ", ".join([brand.name for brand in obj.brands.all()])
    get_brands.short_description = "Thương hiệu"

# admin.site.register(Supplier, SupplierAdmin)

