from rest_framework import serializers
from .models import (
    User, Address, Service, ServiceCategory, ServiceProduct,
    Order, OrderItem, PickupDelivery, Feedback
)

from rest_framework import serializers
from .models import Address
from .utils import parse_delivery_address

from decimal import Decimal
from django.db.models import Sum

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'password': {'required': False, 'write_only': True},
        }

      


class CustomerSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'required': False, 'write_only': True},
            'name': {'required': False},
          
        }

    def get_addresses(self, obj):
        return AddressSerializer(obj.addresses.all(), many=True).data


# class StaffSerializer(serializers.ModelSerializer):
#     addresses = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = '__all__'
#         read_only_fields = ['user_id', 'created_at', 'updated_at']

#     def get_addresses(self, obj):
#         return AddressSerializer(obj.addresses.all(), many=True).data


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class StaffTokenSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer to include user role and mobile_no.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["mobile_no"] = user.mobile_no
        return token


class StaffSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    addresses = serializers.SerializerMethodField()
    picked_orders = serializers.SerializerMethodField()
    delivered_orders = serializers.SerializerMethodField()
    pickup_addresses = serializers.SerializerMethodField()
    delivery_addresses = serializers.SerializerMethodField()
    
    

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True, "required": False},  # <-- make optional
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)  # optional
        groups = validated_data.pop("groups", [])
        user_permissions = validated_data.pop("user_permissions", [])

        user = User(**validated_data)

        if password:
            user.set_password(password)

        user.role = "staff"
        user.save()

        if groups:
            user.groups.set(groups)

        if user_permissions:
            user.user_permissions.set(user_permissions)

        return user

    def to_internal_value(self, data):
        data = data.copy()
    
        image = data.get("image")
    
       
        if isinstance(image, str):
            data.pop("image", None)
    
        return super().to_internal_value(data)

    def get_addresses(self, obj):
        return AddressSerializer(obj.addresses.all(), many=True).data

    def get_picked_orders(self, obj):
        from laundryapp.models import Order
        orders = Order.objects.filter(picked_by=obj.name)
        return OrderSerializer(orders, many=True).data

    def get_delivered_orders(self, obj):
        from laundryapp.models import Order
        orders = Order.objects.filter(delivered_by=obj.name)
        return OrderSerializer(orders, many=True).data

    def get_pickup_addresses(self, obj):
        from laundryapp.models import Order
        orders = Order.objects.filter(picked_by=obj.name)
        return AddressSerializer([order.address for order in orders], many=True).data

    def get_delivery_addresses(self, obj):
        from laundryapp.models import Order
        orders = Order.objects.filter(delivered_by=obj.name)
        return AddressSerializer([order.address for order in orders], many=True).data

# ----------------------------
# ADDRESS SERIALIZER
# ----------------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "address_id",
            "address_line1",
            "address_line2",
            "landmark",
            "city",
            "pincode",
            "address_type", 
            'is_primary',
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["address_id", "created_at", "updated_at"]



class CustomerRegistrationSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'mobile_no', 'password', 'addresses', 'role', 'status']  # Added user_id, role, status
    
    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', [])
        
        # Set default role and status
        validated_data.setdefault('role', 'customer')
        validated_data.setdefault('status', 'active')
        
        # Default email if not provided
        if not validated_data.get('email'):
            validated_data['email'] = f"{validated_data['mobile_no']}@customer.laundry.com"
        
        # Create user - this will automatically generate user_id
        user = User.objects.create_user(
            mobile_no=validated_data['mobile_no'],
            name=validated_data['name'],
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            role=validated_data.get('role'),
            status=validated_data.get('status')
        )
        
        # Create addresses
        for address_data in addresses_data:
            Address.objects.create(
                user=user,
                **address_data
            )
        
        return user
# ----------------------------
# SERVICE, CATEGORY, PRODUCT SERIALIZERS
# ----------------------------
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ServiceCategorySerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    service_detail = ServiceSerializer(source='service', read_only=True)

    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServiceProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), write_only=True)
    category_detail = ServiceCategorySerializer(source='category', read_only=True)

    class Meta:
        model = ServiceProduct
        fields = '__all__'


# ----------------------------
# ORDER ITEM SERIALIZER
# ----------------------------


# ----------------------------
# ORDER ITEM SERIALIZER
# ----------------------------
from rest_framework import serializers

class OrderItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    service = serializers.CharField(source='service.name', read_only=True)
    order_id = serializers.IntegerField(source='order.order_id', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'order_item_id',
            'order_id',
            'service',
            'category_name',
            'product_name',
            'quantity',
            'price',
            'total_price',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('price', 'total_price')


# ----------------------------
# ORDER SERIALIZER
# ----------------------------
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db.models import Sum

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):

    # ----------------------------
    # USER BASIC INFO
    # ----------------------------
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile_no', read_only=True)

    # ----------------------------
    # ADDRESS & SERVICE
    # ----------------------------
    address_details = AddressSerializer(source='address', read_only=True)
    service = serializers.CharField(source='service.name', read_only=True)

    address_line1 = serializers.SerializerMethodField()
    address_line2 = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    landmark = serializers.SerializerMethodField()
    pincode = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    Token_no = serializers.CharField(required=False)

    # ----------------------------
    # ITEMS
    # ----------------------------
    items = OrderItemSerializer(many=True, read_only=True)

    # ----------------------------
    # WRITE-ONLY FK IDs
    # ----------------------------
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )

    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='address',
        write_only=True
    )

    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )

   
    picked_by_name = serializers.SerializerMethodField()
    delivered_by_name = serializers.SerializerMethodField()
    cancelled_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    # ----------------------------
    # ROLE FIELDS
    # ----------------------------
    picked_by_role = serializers.SerializerMethodField()
    delivered_by_role = serializers.SerializerMethodField()
    cancelled_by_role = serializers.SerializerMethodField()
    created_by_role = serializers.SerializerMethodField()
    updated_by_role = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id',
            'user_id', 'address_id',
            'service', 'service_id',
            'Token_no', 'status', 'total_amount', 
            'address_line1', 'address_line2',
            'city', 'landmark', 'pincode',
            'created_at', 'updated_at',
            'created_by', 'updated_by',
            'picked_at', 'delivered_at', 'cancelled_at',
            'picked_by', 'delivered_by', 'cancelled_by',
            'cancel_reason',
            'user_name', 'user_mobile',
            'address_details', 'items',
            'picked_by_name', 'picked_by_role',
            'delivered_by_name', 'delivered_by_role',
            'cancelled_by_name', 'cancelled_by_role',
            'created_by_name', 'created_by_role',
            'updated_by_name', 'updated_by_role'
        ]

        read_only_fields = [
            'picked_at', 'delivered_at', 'cancelled_at',
            'picked_by', 'delivered_by', 'cancelled_by',
            'created_at', 'updated_at'
        ]

    def get_total_amount(self, obj):
        total = obj.items.aggregate(total=Sum('total_price'))['total']
        return total or Decimal('0.00')

    # ----------------------------
    # SAFE ADDRESS GETTERS
    # ----------------------------
    def get_address_line1(self, obj):
        return obj.address.address_line1 if obj.address else None

    def get_address_line2(self, obj):
        return obj.address.address_line2 if obj.address else None

    def get_city(self, obj):
        return obj.address.city if obj.address else None

    def get_landmark(self, obj):
        return obj.address.landmark if obj.address else None

    def get_pincode(self, obj):
        return obj.address.pincode if obj.address else None

    # ----------------------------
    # COMMON USER FETCHER
    # ----------------------------
    def _get_user(self, value):
        if not value:
            return None

        try:
            UserModel = get_user_model()

            # Already user object
            if hasattr(value, 'name') and hasattr(value, 'role'):
                return value

            # Numeric ID
            if isinstance(value, (int, str)) and str(value).isdigit():
                return UserModel.objects.filter(user_id=int(value)).first()

            # String value
            if isinstance(value, str):

                if value.lower() == "admin":
                    class AdminUser:
                        name = "Admin"
                        role = "admin"
                        user_id = "admin"
                    return AdminUser()

                return (
                    UserModel.objects.filter(mobile_no=value).first()
                    or UserModel.objects.filter(email__iexact=value).first()
                    or UserModel.objects.filter(name__iexact=value).first()
                )

            return None

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"_get_user error: {e}")
            return None

    # ----------------------------
    # NAME RESOLVERS
    # ----------------------------
    def get_picked_by_name(self, obj):
        user = self._get_user(obj.picked_by)
        return getattr(user, 'name', None)

    def get_delivered_by_name(self, obj):
        user = self._get_user(obj.delivered_by)
        return getattr(user, 'name', None)

    def get_cancelled_by_name(self, obj):
        user = self._get_user(obj.cancelled_by)
        return getattr(user, 'name', None)

    def get_created_by_name(self, obj):
        if isinstance(obj.created_by, str):
            return obj.created_by
        user = self._get_user(obj.created_by)
        return getattr(user, 'name', None)


    def get_updated_by_name(self, obj):
        if isinstance(obj.updated_by, str):
            return obj.updated_by
        user = self._get_user(obj.updated_by)
        return getattr(user, 'name', None)


    # ----------------------------
    # ROLE RESOLVERS
    # ----------------------------
    def get_picked_by_role(self, obj):
        user = self._get_user(obj.picked_by)
        return getattr(user, 'role', None)

    def get_delivered_by_role(self, obj):
        user = self._get_user(obj.delivered_by)
        return getattr(user, 'role', None)

    def get_cancelled_by_role(self, obj):
        user = self._get_user(obj.cancelled_by)
        return getattr(user, 'role', None)

    def get_created_by_role(self, obj):
        user = self._get_user(obj.created_by)
        return getattr(user, 'role', None)

    def get_updated_by_role(self, obj):
        user = self._get_user(obj.updated_by)
        return getattr(user, 'role', None)


# ----------------------------
# PICKUP/DELIVERY SERIALIZER
# ----------------------------
class PickupDeliverySerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), write_only=True)
    order_detail = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = PickupDelivery
        fields = '__all__'


# ----------------------------
# FEEDBACK SERIALIZER
# ----------------------------
class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)

    # Write-only IDs
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), source='order', write_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        


class WebsiteAddressSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()

    def save(self, **kwargs):
        user = kwargs.get("user")
        delivery_address = self.validated_data.get("delivery_address", "")
        parsed = parse_delivery_address(delivery_address)
        return Address.objects.create(
            user=user,
            address_line1=parsed["address_line1"],
            address_line2=parsed["landmark"],   
            landmark=parsed["landmark"],
            city=parsed["city"],
            pincode=parsed["pincode"]
        )
from rest_framework import serializers
from .models import Address, Order, OrderItem


class WebsiteIndividualAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'landmark', 'city', 'pincode']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('user')
        validated_data['address_type'] = 'home'
        validated_data['is_primary'] = True
        return super().create(validated_data)


class WebsiteOrderItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "order_item_id",
            "service_name",
            "category_name",
            "product_name",
            "quantity",
            "status",
            "created_at"
        ]

class WebsiteOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_mobile = serializers.CharField(source="user.mobile_no", read_only=True)

  
    items = WebsiteOrderItemSerializer(many=True, read_only=True)

    address_details = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id",
            "status",
            "user_name",
            "user_mobile",
            "address_details",
            "items",
            "created_at"
        ]

    def get_address_details(self, obj):
        address = obj.address
        if not address:
            return None

        return {
            "address_id": address.address_id,
            "address_line1": address.address_line1,
            "address_line2": address.address_line2,
            "landmark": address.landmark,
            "city": address.city,
            "pincode": address.pincode,
            "address_type": address.address_type,
            "is_primary": address.is_primary,
            "created_at": address.created_at,
            "updated_at": address.updated_at
        }
