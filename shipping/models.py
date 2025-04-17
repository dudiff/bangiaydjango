from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default='')
    type = models.CharField(max_length=20, default='tinh')
    name_with_type = models.CharField(max_length=100, default='')
    code = models.CharField(max_length=10, default='00')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name_with_type

class District(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(default='')
    type = models.CharField(max_length=20, default='')
    name_with_type = models.CharField(max_length=100, default='')
    path = models.CharField(max_length=100, default='')
    path_with_type = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=10, default='000')
    parent_code = models.CharField(max_length=10, default='00')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return self.name_with_type

class Ward(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(default='')
    type = models.CharField(max_length=20, default='')
    name_with_type = models.CharField(max_length=100, default='')
    path = models.CharField(max_length=100, default='')
    path_with_type = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=10, default='00000')
    parent_code = models.CharField(max_length=10, default='000')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='wards')

    def __str__(self):
        return self.name_with_type

class ShippingFee(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='shipping_fees')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='shipping_fees', null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='shipping_fees', null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = "Shipping Fee"
        verbose_name_plural = "Shipping Fees"

    def __str__(self):
        if self.ward:
            return f"Phí ship cho {self.ward.name_with_type}: {self.fee:,}đ"
        if self.district:
            return f"Phí ship cho {self.district.name_with_type}: {self.fee:,}đ"
        return f"Phí ship cho {self.city.name_with_type}: {self.fee:,}đ"


class ShippingInfo(models.Model):
    cart = models.OneToOneField('cart.Cart', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    is_temporary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipping Info for {self.full_name}"