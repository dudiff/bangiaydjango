from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

def get_default_valid_to():
    return timezone.now() + timedelta(days=30)

class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Phần trăm'),
        ('fixed', 'Số tiền cố định'),
    )
    
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã giảm giá')
    description = models.TextField(verbose_name='Mô tả', default='')
    discount_type = models.CharField(
        max_length=10, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default='percentage',
        verbose_name='Loại giảm giá'
    )
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='Giá trị giảm'
    )
    min_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        default=0,
        verbose_name='Giá trị đơn hàng tối thiểu'
    )
    max_discount = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True,
        verbose_name='Giảm giá tối đa'
    )
    valid_from = models.DateTimeField(verbose_name='Có hiệu lực từ')
    valid_to = models.DateTimeField(verbose_name='Có hiệu lực đến', default=get_default_valid_to)
    is_active = models.BooleanField(default=True, verbose_name='Còn hiệu lực')
    usage_limit = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name='Giới hạn sử dụng'
    )
    times_used = models.IntegerField(default=0, verbose_name='Số lần đã sử dụng')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to='promotions/',
        null=True,
        blank=True,
        verbose_name='Hình ảnh banner'
    )

    class Meta:
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Mã giảm giá'

    def __str__(self):
        return self.code

    def is_valid(self, cart_total=None):
        now = timezone.now()
        
        if not self.is_active:
            return False, "Mã giảm giá không còn hiệu lực"
            
        if now < self.valid_from:
            return False, "Mã giảm giá chưa có hiệu lực"
            
        if now > self.valid_to:
            return False, "Mã giảm giá đã hết hạn"
            
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False, "Mã giảm giá đã hết lượt sử dụng"
            
        if cart_total and cart_total < self.min_purchase:
            return False, f"Đơn hàng tối thiểu {self.min_purchase}đ"
            
        return True, "Mã giảm giá hợp lệ"

    def remove_usage(self):
        """Decrement times_used when promotion is removed"""
        if self.times_used > 0:
            self.times_used -= 1
            self.save()

    def apply_usage(self):
        """Increment times_used only when order is completed"""
        self.times_used += 1
        self.save()

    def calculate_discount(self, cart_total):
        if self.discount_type == 'percentage':
            discount = cart_total * (self.discount_value / 100)
        else:
            discount = self.discount_value

        if self.max_discount:
            discount = min(discount, self.max_discount)

        return min(discount, cart_total)