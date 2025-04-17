from django.db import models
from django.db.models import Sum
from django.conf import settings
from userauths.models import User  # Import the User model from userauth
import datetime  # Import datetime module
from shipping.models import ShippingInfo, City, District, Ward   # Adjust the import path based on your project structure
from django.utils import timezone  # Add this import
from products.models import ProductSizeInventory

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao thành công'),
        ('cancelled', 'Đã hủy'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản ngân hàng'),
        ('vnpay', 'VNPAY'),
        ('momo', 'MOMO'),
    ]

    # Core fields
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')  # Updated to use User from userauth
    order_code = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')  # Provide a default value
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    vnpay_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    momo_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    # Financials
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    # Shipping details
    shipping_name = models.CharField(max_length=255, null=True)
    shipping_email = models.EmailField(null=True)
    shipping_phone = models.CharField(max_length=20, null=True)
    shipping_address = models.TextField(default='Unknown Address')
    shipping_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    shipping_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    shipping_ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    order_date = models.DateTimeField(auto_now_add=True)
    # Update the created_at field
    created_at = models.DateTimeField(default=timezone.now)  # Changed from datetime.date.today
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_code} by {self.user.full_name}"  # Use 'full_name' property
        
    def save(self, *args, **kwargs):
        if not self.order_code:
            last_order = Order.objects.order_by('-id').first()
            if last_order and last_order.order_code.startswith("DSTORE-"):
                last_number = int(last_order.order_code[7:])
                self.order_code = f"DSTORE-{str(last_number + 1).zfill(6)}"
            else:
                self.order_code = "DSTORE-000001"
        super().save(*args, **kwargs)
        
    def get_total_with_shipping(self):
        """Return the total amount including shipping fee"""
        return float(self.total_amount)  # shipping fee is already included in total_amount
    @classmethod
    def generate_order_code(cls):
        last_order = cls.objects.order_by('-id').first()
        if last_order and last_order.order_code.startswith("DSTORE-"):
            last_number = int(last_order.order_code[7:])
            return f"DSTORE-{str(last_number + 1).zfill(6)}"
        return "DSTORE-000001"

    @classmethod
    def create_from_cart(cls, cart, payment_method):
        try:
            # Try to get shipping info first
            shipping_info = ShippingInfo.objects.filter(cart=cart).latest('id')
            
            # Get city, district, ward objects
            city = City.objects.get(id=shipping_info.city_id)
            district = District.objects.get(id=shipping_info.district_id)
            ward = Ward.objects.get(id=shipping_info.ward_id)
            
            shipping_name = shipping_info.full_name
            shipping_email = shipping_info.email
            shipping_phone = shipping_info.phone
            shipping_address = shipping_info.address
            
        except (ShippingInfo.DoesNotExist, City.DoesNotExist, District.DoesNotExist, Ward.DoesNotExist) as e:
            print(f"Error getting shipping info: {str(e)}")
            # Fall back to user profile data
            profile = cart.user.profile
            city = profile.city
            district = profile.district
            ward = profile.ward
            
            shipping_name = profile.full_name
            shipping_email = cart.user.email
            shipping_phone = profile.phone
            shipping_address = profile.address

        # Create formatted address
        address_parts = [
            f"Họ và tên: {shipping_name}",
            f"Email: {shipping_email}",
            f"Số điện thoại: {shipping_phone}",
            f"Địa chỉ: {shipping_address}",
            f"Phường/Xã: {ward.name_with_type if ward else ''}",
            f"Quận/Huyện: {district.name_with_type if district else ''}",
            f"Tỉnh/Thành phố: {city.name_with_type if city else ''}"
        ]
        formatted_address = "\n".join(filter(None, address_parts))
        
        order = cls.objects.create(
            user=cart.user,
            order_code=cls.generate_order_code(),
            payment_method=payment_method,
            shipping_fee=cart.shipping_fee,
            total_amount=cart.get_total(),  # Use get_total() instead of get_final_total()
            shipping_name=shipping_name,
            shipping_email=shipping_email,
            shipping_phone=shipping_phone,
            shipping_address=formatted_address,
            shipping_city=city,
            shipping_district=district,
            shipping_ward=ward
        )

        # Create order items and update both total stock and size inventory
        for cart_item in cart.items.all():
            # Check inventory before creating order item
            if not cart_item.product.check_inventory(cart_item.size, cart_item.quantity):
                raise Exception(f"Không đủ số lượng cho size {cart_item.size.name}")
            size_inventory = ProductSizeInventory.objects.get(
                    product=cart_item.product,
                    size=cart_item.size
                )
            OrderItem.objects.create(
                order=order,
                product_id=cart_item.product.id,
                product_code=str(cart_item.product.id),
                product_name=cart_item.product.name,
                size=cart_item.size,
                color=cart_item.color,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                total_price=cart_item.get_total()
            )
            # Update inventory and total stock
            size_inventory.quantity -= cart_item.quantity
            size_inventory.save()
            cart_item.product.update_total_stock()
            
        return order
            
        # except ShippingInfo.DoesNotExist:
        #     print("No shipping info found for cart")
        #     raise
        # except (City.DoesNotExist, District.DoesNotExist, Ward.DoesNotExist) as e:
        #     print(f"Error getting location data: {str(e)}")
        #     raise
    @staticmethod
    def get_formatted_address(cart, request):
        """Get formatted address from request or profile"""
        if request:
            try:
                # Get shipping info from the database
                shipping_info = ShippingInfo.objects.filter(cart=cart).latest('id')
                
                city = City.objects.get(id=shipping_info.city_id)
                district = District.objects.get(id=shipping_info.district_id)
                ward = Ward.objects.get(id=shipping_info.ward_id)
                
                # Build address string
                address_parts = []
                if shipping_info.full_name:
                    address_parts.append(f"Họ và tên: {shipping_info.full_name}")
                if shipping_info.email:
                    address_parts.append(f"Email: {shipping_info.email}")
                if shipping_info.phone:
                    address_parts.append(f"Số điện thoại: {shipping_info.phone}")
                if shipping_info.address:
                    address_parts.append(f"Địa chỉ: {shipping_info.address}")
                if ward:
                    address_parts.append(f"Phường/Xã: {ward.name_with_type}")
                if district:
                    address_parts.append(f"Quận/Huyện: {district.name_with_type}")
                if city:
                    address_parts.append(f"Tỉnh/Thành phố: {city.name_with_type}")
    
                return "\n".join(address_parts)
    
            except (ShippingInfo.DoesNotExist, City.DoesNotExist, District.DoesNotExist, Ward.DoesNotExist) as e:
                print(f"Error getting shipping info: {str(e)}")
                # Fall back to profile address if shipping info not found
        # Fall back to profile address
        profile = cart.user.profile
        address_parts = []
        if profile.full_name and profile.full_name != "None":
            address_parts.append(f"Họ và tên: {profile.full_name}")
        if profile.user.email:
            address_parts.append(f"Email: {profile.user.email}")
        if profile.phone:
            address_parts.append(f"Số điện thoại: {profile.phone}")
        if profile.address:
            address_parts.append(f"Địa chỉ: {profile.address}")
        if profile.ward:
            address_parts.append(f"Phường/Xã: {profile.ward.name_with_type}")
        if profile.district:
            address_parts.append(f"Quận/Huyện: {profile.district.name_with_type}")
        if profile.city:
            address_parts.append(f"Tỉnh/Thành phố: {profile.city.name_with_type}")
    
        return "\n".join(address_parts)

    def update_delivery_status(self, user):
        """Method for users to confirm delivery"""
        if self.user == user and self.status == 'shipping':  # Changed from 'shipped' to 'shipping'
            self.status = 'delivered'
            if self.payment_method == 'cod':
                self.payment_status = 'paid'
            self.save()
            return True
        return False
    
    def can_confirm_delivery(self):
        """Check if order can be confirmed as delivered"""
        return self.status == 'shipping'  # Changed from 'shipped' to 'shipping'

    def admin_update_status(self, new_status, admin_user):
        """Method for admin to update order status"""
        if admin_user.is_staff:
            self.status = new_status
            self.save()
            return True
        return False

    @property
    def display_total_amount(self):
        return int(self.total_amount)

    @property
    def display_shipping_fee(self):
        return int(self.shipping_fee)
    def cancel_order(self):
        """Cancel order and restore inventory"""
        if self.status in ['pending', 'processing']:
            # Restore inventory for each order item
            for item in self.order_items.all():
                try:
                    size_inventory = ProductSizeInventory.objects.get(
                        product_id=item.product_id,
                        size=item.size
                    )
                    # Restore quantity
                    size_inventory.quantity += item.quantity
                    size_inventory.save()
                    
                    # Update product total stock
                    from products.models import Product
                    product = Product.objects.get(id=item.product_id)
                    product.update_total_stock()
                except ProductSizeInventory.DoesNotExist:
                    continue

            self.status = 'cancelled'
            if self.payment_status == 'paid':
                self.payment_status = 'refunded'
            self.save()
            return True
        return False
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    size = models.ForeignKey('products.Size', 
                            on_delete=models.SET_NULL, 
                            null=True,
                            related_name='order_items_size')
    color = models.ForeignKey('products.ColorType', 
                             on_delete=models.SET_NULL, 
                             null=True,
                             related_name='order_items_color')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=0)
    promotions = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    total_price = models.DecimalField(max_digits=11, decimal_places=0)
    product_id = models.IntegerField(default=0)

    class Meta:
        db_table = 'orders_orderitem'

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size.name if self.size else 'N/A'}) in Order {self.order.order_code}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        return int(self.price)

    @property
    def display_total_price(self):
        return int(self.total_price)

    @property
    def display_promotions(self):
        return int(self.promotions)

    @classmethod
    def get_best_sellers(cls, limit=8):
        """Get best-selling products based on order quantities"""
        return cls.objects.values('product_id')\
            .annotate(total_sold=Sum('quantity'))\
            .order_by('-total_sold')[:limit]