from django.contrib import admin
from .models import ImportOrder, ImportOrderItem
from django import forms
from products.models import Size

class ImportOrderItemForm(forms.ModelForm):
    class Meta:
        model = ImportOrderItem
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If we have an instance with a product, filter sizes
        if self.instance and self.instance.product_id:
            self.fields['size'].queryset = self.instance.product.sizes.all()
        else:
            # Otherwise, show all sizes initially
            self.fields['size'].queryset = Size.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        size = cleaned_data.get('size')
        
        if product and not size:
            # If product is selected but size is not, try to get the first available size
            if product.sizes.exists():
                cleaned_data['size'] = product.sizes.first()
            else:
                self.add_error('size', 'Please select a size for this product')
        
        return cleaned_data

class ImportOrderItemInline(admin.TabularInline):
    model = ImportOrderItem
    form = ImportOrderItemForm
    extra = 0  # No extra empty forms
    readonly_fields = ['product', 'size', 'quantity', 'purchase_price', 'subtotal']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class ImportOrderAdmin(admin.ModelAdmin):
    inlines = [ImportOrderItemInline]
    list_display = ['id', 'supplier', 'created_by', 'created_at', 'total_amount']
    readonly_fields = ['supplier', 'created_by', 'created_at', 'notes', 'total_amount']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        js = ('js/import_order_admin.js',)

admin.site.register(ImportOrder, ImportOrderAdmin)