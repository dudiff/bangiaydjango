from django.db import models
from django.conf import settings
from products.models import Product, Size, ColorType

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('vnpay', 'Thanh toán VNPAY'),
        ('momo', 'Thanh toán MoMo'), 
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                           on_delete=models.CASCADE,
                           related_name='checkout_orders')  # Added related_name
    order_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Đơn hàng #{self.order_code}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            last_order = Order.objects.order_by('-id').first()
            if last_order and last_order.order_code.startswith("DSTORE-"):
                last_number = int(last_order.order_code[7:])
                self.order_code = f"DSTORE-{str(last_number + 1).zfill(6)}"
            else:
                self.order_code = "DSTORE-000001"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, 
                              on_delete=models.CASCADE,
                              related_name='checkout_items')  # Added related_name
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(ColorType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} trong {self.order}"

    @property
    def total(self):
        return self.quantity * self.price
