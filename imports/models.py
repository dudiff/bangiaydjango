from django.db import models
from django.conf import settings
from products.models import Product, Supplier, ProductSizeInventory, Size
from django.core.exceptions import ValidationError
from django.utils import timezone

class ImportOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Nhà cung cấp")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Tổng tiền")

    def __str__(self):
        return f"Đơn nhập hàng #{self.id} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Đơn nhập hàng"
        verbose_name_plural = "Đơn nhập hàng"
        ordering = ['-created_at']

class ImportOrderItem(models.Model):
    import_order = models.ForeignKey(ImportOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    def clean(self):
        # Validate that the size belongs to the product
        if self.product and self.size and not self.product.sizes.filter(id=self.size.id).exists():
            # If the size doesn't exist for this product, add it
            self.product.sizes.add(self.size)
        
        # Ensure size is set
        if not self.size and self.product and self.product.sizes.exists():
            # Set to first available size if none selected
            self.size = self.product.sizes.first()
        
        super().clean()

    def save(self, *args, **kwargs):
        # Convert to appropriate types before multiplication
        quantity = int(self.quantity) if isinstance(self.quantity, str) else self.quantity
        price = float(self.purchase_price) if isinstance(self.purchase_price, str) else self.purchase_price
        
        # Calculate subtotal before saving
        self.subtotal = quantity * price
        
        super().save(*args, **kwargs)

        if self.quantity > 0:
            # Update inventory
            inventory, created = ProductSizeInventory.objects.get_or_create(
                product=self.product,
                size=self.size,
                defaults={'quantity': 0}
            )
            inventory.quantity += self.quantity
            inventory.save()

            # Update product price
            if self.purchase_price:
                self.product.purchase_price = self.purchase_price
                self.product.save()
        
        # Update total amount of import order
        self.import_order.total_amount = sum(item.subtotal for item in self.import_order.items.all())
        self.import_order.save()

    def __str__(self):
        size_name = self.size.name if hasattr(self, 'size') and self.size else "Unknown Size"
        product_name = self.product.name if hasattr(self, 'product') and self.product else "Unknown Product"
        return f"{product_name} - Size {size_name} - {self.quantity} cái"

    class Meta:
        verbose_name = "Chi tiết đơn nhập"
        verbose_name_plural = "Chi tiết đơn nhập"