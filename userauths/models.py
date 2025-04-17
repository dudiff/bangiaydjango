from django.db import models
from django.contrib.auth.models import AbstractUser
from shipping.models import City, District, Ward

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def favorite_products(self):
        return [item.product for item in self.user_favorites.all()]

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey('shipping.City', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('shipping.District', on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey('shipping.Ward', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"