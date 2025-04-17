from django.db import models
import os
from uuid import uuid4
from django.conf import settings 
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rembg import remove
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Category(models.Model):
    GENDER_TYPES = [
        ('1', 'Nam'),
        ('2', 'Nữ'),
        ('3', 'Trẻ em'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    category_type = models.CharField(
        max_length=50,
        choices=GENDER_TYPES,
        verbose_name="Loại danh mục",
        default='1'  # Default to 'Nam'
    )

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

class ShoeType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kiểu giày")

    def __str__(self):
        return self.name

class ColorType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Màu sắc")
    code = models.CharField(max_length=50, verbose_name="Mã màu", help_text="Ví dụ: #FF0000", default="#000000")

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Kích cỡ")

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=255, verbose_name="Chất liệu")

    def __str__(self):
        return self.name

class UsePurpose(models.Model):
    PURPOSE_TYPES = [
        ('1', 'Nam'),
        ('2', 'Nữ'),
        ('3', 'Trẻ em'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Mục đích sử dụng")
    purpose_types = models.CharField(max_length=50, verbose_name="Loại mục đích", 
                                     help_text="Chọn các loại phù hợp, phân cách bằng dấu phẩy (vd: 1,2)")
    
    def has_gender_type(self, gender_code):
        """Check if this purpose includes a specific gender code"""
        if not self.purpose_types:
            return False
        return str(gender_code) in [t.strip() for t in self.purpose_types.split(',')]
    
    def get_purpose_types_display(self):
        """Trả về danh sách đầy đủ các loại mục đích theo chữ"""
        type_dict = dict(self.PURPOSE_TYPES)
        selected_types = [type_dict[t.strip()] for t in self.purpose_types.split(',') if t.strip() in type_dict]
        return f"{self.name}: " + ", ".join(selected_types)
    
    def __str__(self):
        return self.get_purpose_types_display()

class Brand(models.Model):
    BRAND_TYPES = [
        ('1', 'Nam'),
        ('2', 'Nữ'),
        ('3', 'Trẻ em'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Tên thương hiệu")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="Logo") 
    website_url = models.URLField(blank=True, null=True, verbose_name="Website")
    brand_types = models.CharField(
        max_length=50, 
        verbose_name="Loại thương hiệu",
        help_text="Chọn các loại phù hợp, phân cách bằng dấu phẩy (vd: 1,2)",
        default='1',  # Changed to string
        null=True,    # Added to handle null values
        blank=True    # Added to handle blank values
    )

    def get_brand_types_display(self):
        if not self.brand_types:
            return "Không xác định"
        
        # Convert to string and handle both integer and string inputs
        if isinstance(self.brand_types, (int, str)):
            brand_types_list = str(self.brand_types).split(',')
            type_dict = dict(self.BRAND_TYPES)
            selected_types = [type_dict[t.strip()] for t in brand_types_list if t.strip() in type_dict]
            return ", ".join(selected_types) if selected_types else "Không xác định"
        return "Không xác định"

    def __str__(self):
        return f"{self.name} ({self.get_brand_types_display()})"
        
LABEL_CHOICES = [
    ('sale', 'Sale'),
    ('hot', 'Hot'),
    ('new', 'New')
]

def product_image_path(instance, filename):
    """Tạo đường dẫn lưu ảnh theo mã sản phẩm"""
    ext = filename.split('.')[-1]
    filename = f"{instance.product_code}.{ext}" if instance.product_code else f"{uuid4().hex}.{ext}"
    return os.path.join('products', filename)

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá bán")
    sale_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="Giá khuyến mãi")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, default=0, verbose_name="Giá nhập")
    stock = models.IntegerField(verbose_name="Tồn kho")
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name="Hình ảnh")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, verbose_name="Danh mục")
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE, verbose_name="Thương hiệu")
    shoe_type = models.ForeignKey("ShoeType", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Loại giày")
    material = models.ForeignKey("Material", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Chất liệu")
    use_purpose = models.ForeignKey("UsePurpose", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Mục đích sử dụng")
    product_code = models.CharField(max_length=10, unique=True, blank=True, verbose_name="Mã sản phẩm")
    colors = models.ManyToManyField("ColorType", blank=True, verbose_name="Màu sắc")
    sizes = models.ManyToManyField(
        "Size",
        blank=True,
        verbose_name="Kích cỡ"
    )
    labels = models.CharField(max_length=10, choices=LABEL_CHOICES, blank=True, null=True, verbose_name="Nhãn")
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Nhà cung cấp")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.product_code:
            product_type_prefix = self.get_product_type_prefix()
            last_product = Product.objects.filter(product_code__startswith=product_type_prefix).order_by('id').last()
            next_number = 1 if not last_product else int(last_product.product_code[1:]) + 1
            self.product_code = f"{product_type_prefix}{next_number:05d}"
        # Process image if it exists
        if self.image and hasattr(self.image, 'file'):
            # Open image
            img = Image.open(self.image)
            
            # Remove background
            output = remove(img)
            
            # Save to BytesIO
            temp_thumb = BytesIO()
            output.save(temp_thumb, format='PNG')
            temp_thumb.seek(0)
            
            # Save the processed image
            self.image.save(
                self.image.name,
                ContentFile(temp_thumb.read()),
                save=False
            )
        
        super().save(*args, **kwargs)
        
        if is_new:
            # Create inventory records for new products
            for size in self.sizes.all():
                ProductSizeInventory.objects.get_or_create(
                    product=self,
                    size=size,
                    defaults={'quantity': 0}
                )

    def add_size(self, size):
        """Add a new size and create its inventory"""
        self.sizes.add(size)
        # Create inventory record when adding new size
        ProductSizeInventory.objects.get_or_create(
            product=self,
            size=size,
            defaults={'quantity': 0}
        )

    def remove_size(self, size):
        """Remove a size and its inventory"""
        self.sizes.remove(size)
        # Delete inventory record when removing size
        ProductSizeInventory.objects.filter(
            product=self,
            size=size
        ).delete()

    def get_size_inventory(self, size):
        try:
            inventory = self.size_inventory.get(size=size)
            return inventory.quantity
        except ProductSizeInventory.DoesNotExist:
            return 0

    def is_size_available(self, size):
        return self.get_size_inventory(size) > 0

    def update_total_stock(self):
        self.stock = sum(inv.quantity for inv in self.size_inventory.all())
        self.save()
    def check_inventory(self, size, quantity):
        """Check if there's enough inventory for a specific size"""
        try:
            inventory = ProductSizeInventory.objects.get(
                product=self,
                size=size
            )
            return inventory.quantity >= quantity
        except ProductSizeInventory.DoesNotExist:
            return False

    def get_available_sizes(self):
        """Get list of sizes with available inventory"""
        return Size.objects.filter(
            productsizeinventory__product=self,
            productsizeinventory__quantity__gt=0
        )
    def get_product_type_prefix(self):
        category_mapping = {
            'nu': 'G',
            'nam': 'N',
            'tre em': 'K'
        }
        # Chuẩn hóa tên category: bỏ dấu, lowercase, bỏ khoảng trắng
        category_name = self.category.name.lower()
        category_name = category_name.replace('ữ', 'u').replace('à', 'a').replace('ẻ', 'e')
        category_name = ''.join(c for c in category_name if not c.isspace())
        
        # Debug print
        print(f"Current category name: {self.category.name}")
        print(f"After processing: {category_name}")
        
        return category_mapping.get(category_name, 'N')

    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    def get_rating_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    """Lưu nhiều ảnh phụ cho sản phẩm"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Sản phẩm")
    image = models.ImageField(upload_to="products/", verbose_name="Hình ảnh")

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            # Open image
            img = Image.open(self.image)
            
            # Remove background
            output = remove(img)
            
            # Save to BytesIO
            temp_thumb = BytesIO()
            output.save(temp_thumb, format='PNG')
            temp_thumb.seek(0)
            
            # Save the processed image
            self.image.save(
                self.image.name,
                ContentFile(temp_thumb.read()),
                save=False
            )
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"
class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên nhà cung cấp")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ")
    brands = models.ManyToManyField(Brand, verbose_name="Thương hiệu", blank=True)
    
    def __str__(self):
        return self.name
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Sản phẩm")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người dùng")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Đánh giá")
    comment = models.TextField(verbose_name="Bình luận", default="No comment provided")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"
class ProductSizeInventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='size_inventory', verbose_name="Sản phẩm")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Kích cỡ")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng")

    class Meta:
        unique_together = ('product', 'size')
        verbose_name = "Tồn kho theo size"
        verbose_name_plural = "Tồn kho theo size"

    def __str__(self):
        return f"{self.product.name} - Size {self.size.name}: {self.quantity}"

    def get_available_sizes(self, product):
        """Get only sizes that are linked to this product"""
        return product.sizes.all()

@receiver(m2m_changed, sender=Product.sizes.through)
def handle_product_sizes_change(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        # Create inventory records for newly added sizes
        for size_id in pk_set:
            ProductSizeInventory.objects.get_or_create(
                product=instance,
                size_id=size_id,
                defaults={'quantity': 0}
            )
    elif action == "post_remove":
        # Remove inventory records for removed sizes
        ProductSizeInventory.objects.filter(
            product=instance,
            size_id__in=pk_set
        ).delete()

# Make sure to connect the signal at the bottom of models.py
m2m_changed.connect(handle_product_sizes_change, sender=Product.sizes.through)