# laundryapp/utils.py
from datetime import datetime, timedelta
from django.conf import settings
import jwt

# --------------------------
# Convert Order Status
# --------------------------
def convert_order_status(status: str) -> str:
    """Convert order status codes to readable form."""
    mapping = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'picked': 'Picked',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
        'rejected': 'Rejected',
    }
    return mapping.get(status.lower(), status)

# --------------------------
# Convert Service Type (Pickup/Delivery)
# --------------------------
def convert_service_type(service_type: str) -> str:
    mapping = {
        'pickup': 'Pickup',
        'delivery': 'Delivery',
    }
    return mapping.get(service_type.lower(), service_type)

# --------------------------
# Convert Category Name (example)
# --------------------------
def convert_category_name(category: str) -> str:
    mapping = {
        "mens_clothing": "Men's Clothing",
        "womens_clothing": "Women's Clothing",
        "kids_clothing": "Kids Clothing",
        "house_holds": "House Holds",
        "others": "Others"
    }
    return mapping.get(category.lower(), category)

# --------------------------
# Convert Product Name (example)
# --------------------------
def convert_product_name(product: str) -> str:
    mapping = {
        "t_shirt": "T-Shirt",
        "shirt": "Shirt",
        "jeans": "Jeans",
        "trousers": "Trousers",
        "saree": "Saree",
        "kurti": "Kurti",
        # Add more product mappings as needed
    }
    return mapping.get(product.lower(), product)

# --------------------------
# JWT Token Generation
# --------------------------
from rest_framework_simplejwt.tokens import RefreshToken

def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }
# --------------------------
# Created By Identifier
# --------------------------
def get_created_by_identifier(user) -> str:
    """Return a string identifier for who created/updated a record."""
    if user.role.lower() in ["admin", "staff"]:
        return f"{user.role.title()}: {user.name}"
    else:
        return f"Customer: {user.name}"





import re

def parse_delivery_address(address):
    landmark = ""
    city = ""
    pincode = ""
    address_line1 = address

    # Extract landmark: "Landmark: xyz"
    landmark_match = re.search(r"landmark\s*:\s*([^,]+)", address, re.IGNORECASE)
    if landmark_match:
        landmark = landmark_match.group(1).strip()
        address_line1 = address.replace(landmark_match.group(0), "")

    # Extract city & pincode: "city - 123456"
    city_pin_match = re.search(r"([A-Za-z\s]+)\s*-\s*(\d{6})", address)
    if city_pin_match:
        city = city_pin_match.group(1).strip()
        pincode = city_pin_match.group(2).strip()
        address_line1 = address_line1.replace(city_pin_match.group(0), "")

    # Clean extra commas/spaces
    address_line1 = address_line1.replace(",", "").strip()

    return {
        "address_line1": address_line1,
        "landmark": landmark,
        "city": city or "Unknown",
        "pincode": pincode or ""
    }

        
from django.contrib.auth.backends import ModelBackend

class IgnoreIsActiveBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True
