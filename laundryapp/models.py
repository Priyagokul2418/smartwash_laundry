from django.db import models
from django.utils import timezone
import string
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from decimal import Decimal
from django.db.models import Sum


# ------------------------------
# User Model
# # ------------------------------
# class UserManager(BaseUserManager):
#     def create_user(self, mobile_no, password=None, **extra_fields):
#         if not mobile_no:
#             raise ValueError("The Mobile number must be set")

#         user = self.model(mobile_no=mobile_no, **extra_fields)

#         if password:
#             user.set_password(password)
#         else:
#             user.set_unusable_password()   # <-- makes password optional

#         user.save(using=self._db)
#         return user

#     def create_superuser(self, mobile_no, password=None, **extra_fields):
#         extra_fields.setdefault('role', 'admin')
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('status', 'active')

#         # superuser MUST have a password
#         if not password:
#             raise ValueError("Superusers must have a password.")

#         return self.create_user(mobile_no, password, **extra_fields)

from django.db import models
from django.utils import timezone
import string
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation



class UserManager(BaseUserManager):
    def create_user(self, mobile_no, password=None, **extra_fields):
        if not mobile_no:
            raise ValueError('Mobile number is required')

        # DO NOT force role to customer — keep what frontend sends
        # role = extra_fields.pop('role', 'customer')

        user = self.model(
            mobile_no=mobile_no,
            **extra_fields
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_no, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile_no, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'

    class UserStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        SUSPENDED = 'suspended', 'Suspended'

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, null=True, blank=True, db_index=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.ADMIN)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    otp_code = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)

    # ✅ This is what Django checks for authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    addresses = GenericRelation(
        'Address',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='user_addresses'
    )

    USERNAME_FIELD = 'mobile_no'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        # ✅ Sync is_active with status
        self.is_active = True if self.status == self.UserStatus.ACTIVE else False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.mobile_no})"

    @property
    def id(self):
        return self.user_id

# ------------------------------
# Address Model
# ------------------------------
class Address(models.Model):
    address_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    blank=True,
    related_name="addresses"
)
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, null=True)
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='home',
        help_text="Specify whether the address is home, work, or other"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Mark this address as primary"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if self.is_primary:
            Address.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.address_line1} - {self.city}"






class Customer(models.Model):


    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, blank=True, null=True)
    addresses = GenericRelation(Address, related_query_name="customer")
    image_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # # User authentication field
    # USERNAME_FIELD = 'mobile_no'
    # REQUIRED_FIELDS = ['name']

   

    def __str__(self):
        return f"{self.name} ({self.mobile_no})"

    @property
    def addresses(self):
        return Address.objects.filter(customer_id=self.user_id)


class Staff(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    ]

    user_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True,null=True,blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)

    role = models.CharField(max_length=20, default='Staff')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    image_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    addresses = GenericRelation(Address, related_query_name="staff")

    # USERNAME_FIELD = 'mobile_no'
    # REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"



# ------------------------------
# Service Models
# ------------------------------
class Service(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceProduct(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)
    image_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ------------------------------
# Order Models
# ------------------------------

class Order(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PICKED = 'picked', 'Picked'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REJECTED = 'rejected', 'Rejected'

    order_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='orders', null=True, blank=True
    )
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='orders'
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='orders'
    )

    Token_no = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    confirmed_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    picked_by = models.CharField(max_length=150, null=True, blank=True)
    delivered_by = models.CharField(max_length=150, null=True, blank=True)
    cancelled_by = models.CharField(max_length=150, null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, null=True, blank=True)
    updated_by = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Order {self.Token_no}"

    def calculate_total_amount(self):
        total = self.items.aggregate(
            total=Sum('total_price')
        )['total']
        return total or Decimal('0.00')

    # ONLY status logic here
    def save(self, *args, **kwargs):
        if self.status == self.OrderStatus.CONFIRMED and not self.confirmed_at:
            self.confirmed_at = timezone.now()

        if self.status == self.OrderStatus.PICKED and not self.picked_at:
            self.picked_at = timezone.now()

        if self.status == self.OrderStatus.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()

        if self.status == self.OrderStatus.CANCELLED and not self.cancelled_at:
            self.cancelled_at = timezone.now()

        super().save(*args, **kwargs)


class OrderItem(models.Model):

    order_item_id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='order_items'
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name='order_items'
    )
    product = models.ForeignKey(
        ServiceProduct, on_delete=models.CASCADE, related_name='order_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    status = models.CharField(
        max_length=50,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, null=True, blank=True)
    updated_by = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'category', 'product'],
                name='uq_order_item'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price

        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"



# ------------------------------
# Pickup & Delivery Model
# ------------------------------
class PickupDelivery(models.Model):
    class ServiceType(models.TextChoices):
        PICKUP = 'pickup', 'Pickup'
        DELIVERY = 'delivery', 'Delivery'

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='pickup_deliveries')
    scheduled_date = models.DateTimeField()
    actual_date = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=ServiceType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status} - {self.order.Token_no}"


# ------------------------------
# Feedback Model
# ------------------------------
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback for Order {self.order.Token_no}"
