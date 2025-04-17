from django.db import models
from django.conf import settings
from products.models import Product, Size, ColorType  # Update this import line

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    shipping_method = models.CharField(max_length=20, null=True, blank=True)
    shipping_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=0,
        verbose_name="Phí vận chuyển"
    )

    @property
    def shipping_info(self):
        try:
            return self.shippinginfo
        except ShippingInfo.DoesNotExist:
            return None
    shipping_info = models.OneToOneField('shipping.ShippingInfo', on_delete=models.CASCADE, null=True, blank=True, related_name='cart_info')  # Changed related_name
    promotion = models.ForeignKey(
        'promotions.Promotion', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=0
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_completed=False),
                name='unique_active_cart'
            )
        ]

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_subtotal(self):
        """Calculate cart subtotal (before discount and shipping)"""
        return sum(item.get_total() for item in self.items.all())

    def get_total(self):
        """Calculate total before discount but including shipping"""
        return self.get_subtotal() 

    def get_total_with_shipping(self):
        """Calculate total with shipping fee"""
        total = self.get_total()
        if self.shipping_fee is None:
            return total
        return total + self.shipping_fee

    def get_total_with_discount(self):
        """Calculate final total with discount"""
        total = self.get_total()  # Get base total without shipping
        if self.discount:
            total -= self.discount
        if self.shipping_fee:  # Add shipping after discount
            total += self.shipping_fee
        return total
    @classmethod
    def get_active_cart(cls, user):
        cart, _ = cls.objects.get_or_create(
            user=user,
            is_completed=False,
        )
        return cart

    def update_item_quantity(self, product_id, quantity):
        try:
            cart_item = self.items.get(product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            return True
        except CartItem.DoesNotExist:
            return False

    def remove_item(self, item_id):
        try:
            # Get the cart item first
            cart_item = self.items.get(id=item_id)
            
            # Check if this is the last item
            if self.items.count() == 1:
                # If cart has promotion, clear it first
                if self.promotion:
                    self.promotion = None
                    self.discount = 0
                    self.save()
                
                # Delete the item
                cart_item.delete()
                
                # Finally delete the cart itself
                Cart.objects.filter(id=self.id).delete()
            else:
                # If not the last item, just delete the item
                cart_item.delete()
            
            return True
        except CartItem.DoesNotExist:
            return False

    def get_final_total(self):
        """Calculate the final total including shipping and discount"""
        total = self.get_total()
        # Apply discount if any
        if self.discount:
            total -= self.discount
        # Add shipping fee
        if self.shipping_fee:
            total += self.shipping_fee
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    size = models.ForeignKey('products.Size', on_delete=models.CASCADE)
    color = models.ForeignKey('products.ColorType', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product', 'size', 'color')  # Ensure unique combination

    def get_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Size: {self.size.name}, Color: {self.color.name})"