from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
import bcrypt
from django.contrib.auth.hashers import make_password
import json
from .models import (
    Order, OrderItem, Service, ServiceCategory,
    ServiceProduct, User,Address,Customer)
from .serializers import StaffSerializer,CustomerRegistrationSerializer,AddressSerializer, UserSerializer,CustomerSerializer,WebsiteOrderItemSerializer
from .permissions import IsAdminUserOnly
from laundryapp.models import User
from .serializers import StaffSerializer
from .permissions import IsAdminUserOnly
from django.db.models import Q
from django.contrib.auth.hashers import make_password

# from .serializers import LoginSerializer, VerifyOTPSerializer
from .utils import generate_token
import random
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from datetime import datetime
from typing import List
from .models import PickupDelivery
from .serializers import (
    PickupDeliverySerializer,
)
 # Assuming you have enums or choices
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from datetime import timedelta
from django.db.models import Count, Q
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView

from laundryapp.models import Order
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, User
from .serializers import OrderSerializer,OrderItemSerializer,WebsiteAddressSerializer
from .permissions import IsStaffOrAdmin



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Service, ServiceCategory, ServiceProduct
from .serializers import ServiceSerializer, ServiceCategorySerializer, ServiceProductSerializer


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OrderItem
from .serializers import  OrderItemSerializer
from django.shortcuts import get_object_or_404



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
import random
import traceback


from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


class UserView(APIView):
    permission_classes = [AllowAny]  
    # -------------------------
    # GET (all users OR single)
    # -------------------------
    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # -------------------------
    # POST (create user)
    # -------------------------
    def post(self, request):
        data = request.data.copy()  
        
        if User.objects.filter(mobile_no=data.get("mobile_no")).exists():
            return Response(
                {"error": "Mobile number already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if data.get("email") and User.objects.filter(email=data["email"]).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data["password"] = make_password(data.get("password"))

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # PUT (update user)
    # -------------------------
    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)

        data = request.data.copy()

        # Hash new password if provided
        if "password" in data and data["password"]:
            data["password"] = make_password(data["password"])
        else:
            data["password"] = user.password  # keep old password

        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # DELETE (remove user)
    # -------------------------
    def delete(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from .models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
# Create a new file: views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import json
from .models import User


from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
import json

@method_decorator(csrf_exempt, name='dispatch')   # Disable CSRF for this view
class AdminLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            # -----------------------------
            # Parse JSON (DRF handles this)
            # -----------------------------
            try:
                data = request.data
                if not isinstance(data, dict):
                    raise ValueError("Invalid JSON")
            except:
                return Response({"error": "Invalid JSON body"}, status=400)

            mobile_no = data.get("mobile_no")
            password = data.get("password")

            if not mobile_no or not password:
                return Response(
                    {"error": "Mobile number and password are required"},
                    status=400
                )

            # -----------------------------
            # Get user
            # -----------------------------
            user = User.objects.filter(mobile_no=mobile_no, role="admin").first()

            if not user:
                return Response({"error": "Admin not found"}, status=404)

            # -----------------------------
            # Validate password
            # -----------------------------
            if not check_password(password, user.password):
                return Response({"error": "Invalid password"}, status=401)

            # -----------------------------
            # Generate JWT
            # -----------------------------
            refresh = RefreshToken.for_user(user)

            response_data = {
                "message": "Admin login successful",
                "admin": {
                    "id": user.user_id,
                    "name": user.name,
                    "mobile_no": user.mobile_no,
                    "email": user.email,
                    "role": user.role,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }

            return Response(response_data, status=200)

        except Exception as e:
            # Show real error for debugging
            print("🔥 SERVER ERROR:", str(e))
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)


import random
from django.http import JsonResponse
from rest_framework.views import APIView
from django.core.cache import cache
   # adjust import

class AdminForgotPassword(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile_no")

        if not mobile:
            return JsonResponse({"error": "Mobile number is required"}, status=400)

        user = User.objects.filter(mobile_no=mobile, role="admin").first()

        if not user:
            return JsonResponse({"error": "Admin not found"}, status=404)

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Store OTP in cache for 5 minutes
        cache.set(f"otp_{mobile}", otp, timeout=300)

        print(f"📲 OTP for {mobile} is {otp}")

        return JsonResponse({"message": "OTP sent to your mobile number"}, status=200)
    

class AdminVerifyOTP(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]  

    def post(self, request):
        mobile = request.data.get("mobile_no")
        otp = request.data.get("otp")

        if not mobile or not otp:
            return JsonResponse({"error": "Mobile and OTP required"}, status=400)

        saved_otp = cache.get(f"otp_{mobile}")

        if not saved_otp:
            return JsonResponse({"error": "OTP expired or invalid"}, status=400)

        if str(saved_otp) != str(otp):
            return JsonResponse({"error": "Invalid OTP"}, status=400)

        # OTP verified. Create temporary token
        temp_token = f"reset_{mobile}_{random.randint(10000,99999)}"

        cache.set(temp_token, mobile, timeout=600)  # valid for 10 minutes

        return JsonResponse({
            "message": "OTP verified",
            "reset_token": temp_token
        })
    
class AdminResendOTP(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]  

    def post(self, request):
        mobile = request.data.get("mobile_no")

        if not mobile:
            return JsonResponse({"error": "Mobile number is required"}, status=400)

        user = User.objects.filter(mobile_no=mobile, role="admin").first()

        if not user:
            return JsonResponse({"error": "Admin not found"}, status=404)

        # Generate new OTP
        otp = random.randint(100000, 999999)

        # Store OTP again for 5 minutes (overwrite previous)
        cache.set(f"otp_{mobile}", otp, timeout=300)

        print(f"🔁 RESEND OTP for {mobile} is {otp}")

        return JsonResponse({"message": "OTP resent successfully"}, status=200)

    
from django.contrib.auth.hashers import make_password

class AdminResetPassword(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]  

    def post(self, request):
        reset_token = request.data.get("reset_token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not reset_token or not new_password or not confirm_password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        mobile = cache.get(reset_token)
        if not mobile:
            return JsonResponse({"error": "Invalid or expired token"}, status=400)

        user = User.objects.filter(mobile_no=mobile, role="admin").first()

        if not user:
            return JsonResponse({"error": "Admin not found"}, status=404)

        # Update password
        user.password = make_password(new_password)
        user.save()

        # Clear token
        cache.delete(reset_token)

        return JsonResponse({"message": "Password reset successful"})
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile_no")
        name = request.data.get("name")
        role = request.data.get("role", "customer")  # Default to customer if not specified
        
        if not mobile:
            return Response(
                {"success": False, "message": "mobile_no is required"}, 
                status=400
            )

        # Check if user exists
        user = User.objects.filter(mobile_no=mobile).first()

        if user:
            # Check user status
            user_status = str(user.status).lower()

            # Blocked/Inactive users
            if user_status in ["blocked", "inactive"]:
                return Response({
                    "success": False,
                    "message": f"User status is {user.status}. Cannot login."
                }, status=403)

            # Active user - Direct login
            if user_status == "active":
                # Generate tokens
                tokens = generate_token(user)

                return Response({
                    "success": True,
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"],
                    "token_type": "bearer",
                    "message": "Login successful",
                    "user_id": user.user_id,
                    "name": user.name,
                    "mobile_no": user.mobile_no,
                    "role": user.role,
                    "auto_login": True
                }, status=200)

        # ---------------------------------------------------------
        # NEW USER - PREVENT STAFF SELF-REGISTRATION
        # ---------------------------------------------------------
        if str(role).lower() == "staff":
            return Response({
                "success": False,
                "message": "Staff accounts cannot be registered by users. Only admin can create staff."
            }, status=403)

        # New user - Create account automatically
        if not name:
            return Response({
                "success": False,
                "message": "Name is required for new users."
            }, status=400)

        # Validate role (only allow customer for self-registration)
        valid_role = "customer"
        if role and str(role).lower() != "customer":
            return Response({
                "success": False,
                "message": f"Only 'customer' role can be self-registered. Your requested role '{role}' is not allowed."
            }, status=403)

        # Create new user
        new_user = User.objects.create(
            mobile_no=mobile,
            name=name,
            status="active",
            role=valid_role,  # Always force to customer for self-registration
            password=make_password(None)  # Set default password
        )

        # Also create Customer record
        Customer.objects.get_or_create(
            mobile_no=mobile,
            defaults={
                "name": name,
                "role": valid_role,
                "status": "active"
            }
        )

        # Generate tokens for new user
        tokens = generate_token(new_user)

        return Response({
            "success": True,
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"],
            "token_type": "bearer",
            "message": "Registration and login successful",
            "user_id": new_user.user_id,
            "name": new_user.name,
            "mobile_no": new_user.mobile_no,
            "role": new_user.role,
            "auto_login": True
        }, status=200)
    



# class LoginView(APIView):
#     permission_classes = []  # public access

#     def post(self, request):
#         mobile = request.data.get("mobile_no")
#         if not mobile:
#             return Response({"success": False, "message": "mobile_no is required"}, status=400)

#         user = User.objects.filter(mobile_no=mobile).first()

#         if user:
#             # Auto-login → generate JWT using SimpleJWT
#           tokens = generate_token(user)
#           return Response({
#                 "success": True,
#                 "access_token": tokens["access"],  
#                 "refresh_token": tokens["refresh"], 
#                 "token_type": "bearer",
#                 "message": "Login successful",
#                 "user_id": user.user_id,
#                 "name": user.name,
#                 "mobile_no": user.mobile_no,
#                 "role": user.role,
#                 "auto_login": True
#             }, status=200)

#         # New user → send OTP
#         otp = str(random.randint(1000, 9999))
#         new_user = User.objects.create(
#             mobile_no=mobile,
#             otp_code=otp,
#             status="pending",
#             role="admin",
#             name=request.data.get('name')
#         )

#         print("OTP =", otp)

#         return Response({
#             "success": True,
#             "message": "OTP sent to mobile number",
#             "mobile_no": mobile,
#             "next_step": "verify_otp",
#             "user_id": new_user.user_id,
#             "auto_login": False
#         }, status=200)

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Customer,Staff

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")
        name = request.data.get("name", None)

        # Validate input
        if not user_id or not otp:
            return Response(
                {"success": False, "message": "user_id and otp are required"},
                status=400
            )

        # Find user
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        # Validate OTP
        if user.otp_code != otp:
            return Response({"success": False, "message": "Invalid OTP"}, status=400)

        # Update only OTP and status
        user.otp_code = None
        user.status = "active"

        # Update name only if provided
        if name:
            user.name = name

        user.save()

        # Create sub-record depending on existing user.role (DO NOT OVERRIDE)
        if user.role == "customer":
            Customer.objects.get_or_create(
                mobile_no=user.mobile_no,
                defaults={
                    "name": user.name,
                    "email": user.email,
                    "role": "customer"
                }
            )

        elif user.role == "staff":
            Staff.objects.get_or_create(
                mobile_no=user.mobile_no,
                defaults={
                    "name": user.name,
                    "email": user.email,
                    "role": "staff"
                }
            )

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "success": True,
            "access_token": access_token,
            "refresh_token": str(refresh),
            "token_type": "bearer",
            "message": "Login successful",
            "user_id": user.user_id,
            "name": user.name,
            "mobile_no": user.mobile_no,
            "role": user.role,  # <-- now correct, no overwrite
            "auto_login": False
        }, status=200)



# ------------------------------
# RESEND OTP VIEW
# ------------------------------
class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile_no")
        if not mobile:
            return Response({"success": False, "message": "mobile_no is required"}, status=400)

        user = User.objects.filter(mobile_no=mobile, status="pending").first()
        if not user:
            return Response({"success": False, "message": "No pending verification found"}, status=404)

        otp = str(random.randint(1000, 9999))
        user.otp_code = otp
        user.save()

        # NOTE: remove otp in production
        print("RESEND OTP =", otp)

        return Response({
            "success": True,
            "message": "A new OTP has been sent successfully.",
            "mobile_no": user.mobile_no,
            "next_step": "verify_otp",
            "cooldown_period": 60,
            "otp": otp
        }, status=200)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch addresses linked to the User
        addresses = Address.objects.filter(user=user).values(
            "address_id",
            "address_line1",
            "address_line2",
            "landmark",
            "address_type",
            "city",
            "pincode"
        )

        # Load Customer/Staff profile
        customer = None
        staff = None

        if user.role == "customer":
            customer = Customer.objects.filter(mobile_no=user.mobile_no).first()

        elif user.role == "staff":
            staff = Staff.objects.filter(mobile_no=user.mobile_no).first()

        return Response({
            "success": True,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "mobile_no": user.mobile_no,
                "role": user.role,
                "status": user.status,
                "image": user.image.url if user.image else None,
                "addresses": list(addresses),
                "customer_profile": {
                    "id": customer.user_id,
                    "name": customer.name,
                    "email": customer.email,
                    "mobile_no": customer.mobile_no,
                    "image_url": customer.image_url,
                    "status": customer.status
                } if customer else None,
                "staff_profile": {
                    "id": staff.user_id,
                    "name": staff.name,
                    "email": staff.email,
                    "mobile_no": staff.mobile_no,
                    "image_url": staff.image_url,
                    "status": staff.status
                } if staff else None
            }
        }, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Address
from .serializers import AddressSerializer

class AddressView(APIView):

    # -----------------------------------------
    # GET (single, all, or by user)
    # -----------------------------------------
    def get(self, request, address_id=None, user_id=None):
        # Get address by ID
        if address_id:
            address = get_object_or_404(Address, pk=address_id)
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get all addresses of a user
        if user_id:
            addresses = Address.objects.filter(user_id=user_id)
            serializer = AddressSerializer(addresses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get all addresses
        addresses = Address.objects.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # -----------------------------------------
    # POST (create a new address for existing user)
    # # -----------------------------------------
    # def post(self, request):
    #     data = request.data.copy()
    #     mobile_no = data.pop("mobile_no", None)

    #     if not mobile_no:
    #         return Response({"error": "mobile_no is required"}, status=400)

    #     # Find existing user
    #     try:
    #         user = User.objects.get(mobile_no=mobile_no)
    #     except User.DoesNotExist:
    #         return Response({"error": "User not found"}, status=404)

    #     # If new address is default, remove default from old ones
    #     if data.get("is_default"):
    #         Address.objects.filter(user=user).update(is_default=False)

    #     serializer = AddressSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save(user=user)  # attach to existing user
    #         return Response(serializer.data, status=201)

    #     return Response(serializer.errors, status=400)
    def post(self, request):
        data = request.data.copy()
        mobile_no = data.get("mobile_no")  # <-- pop() அல்ல, get() use செய்ய

        print(f"📦 Received mobile_no: {mobile_no}")
        print(f"📦 Full data: {data}")
        
        if not mobile_no:
            return Response({"error": "mobile_no is required"}, status=400)

        # Find existing user
        try:
            user = User.objects.get(mobile_no=mobile_no)
            print(f"✅ Found user: {user.user_id} - {user.name}")
        except User.DoesNotExist:
            print(f"❌ User with mobile_no={mobile_no} not found in database")
            # List available mobile numbers
            available = list(User.objects.values_list('mobile_no', flat=True)[:10])
            print(f"📋 Available mobile numbers: {available}")
            return Response({
                "error": f"User with mobile number {mobile_no} not found"
            }, status=404)
        
        # If new address is default, remove default from old ones
        if data.get("is_default"):
            Address.objects.filter(user=user).update(is_default=False)

        serializer = AddressSerializer(data=data)  # <-- data-ல் mobile_no உள்ளது
        if serializer.is_valid():
            serializer.save(user=user)  # attach to existing user
            return Response(serializer.data, status=201)

        print(f"❌ Serializer errors: {serializer.errors}")
        return Response(serializer.errors,status=400)

    # -----------------------------------------
    # PUT (update address)
    # -----------------------------------------
    def put(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id)
        data = request.data.copy()

        # If updating default address, remove default from others
        if data.get("is_default"):
            Address.objects.filter(user_id=address.user_id).update(is_default=False)

        serializer = AddressSerializer(address, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------
    # DELETE (soft delete address)
    # -----------------------------------------
    def delete(self, request, address_id):
        address = get_object_or_404(Address, pk=address_id)
        address.status = "inactive"  # soft delete
        address.save()
        return Response({"message": "Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CustomerAPIView(APIView):
    # ============================
    # GET → list customers or single customer with addresses
    # ============================
    def get(self, request, customer_id=None, address_id=None):
        search = request.query_params.get("search")

        if customer_id:
            # Get specific customer
            customer = get_object_or_404(User, user_id=customer_id, role="customer")
            
            if address_id:
                # Get specific address
                address = get_object_or_404(Address, pk=address_id, user=customer)
                return Response(AddressSerializer(address).data)
            else:
                # Get all addresses for customer
                addresses = Address.objects.filter(user=customer)
                return Response({
                    "customer": CustomerSerializer(customer).data,
                    "addresses": AddressSerializer(addresses, many=True).data
                })

        # Get all customers
        customers = User.objects.filter(role="customer")

        if search:
            customers = customers.filter(
                Q(name__icontains=search) |
                Q(mobile_no__icontains=search) |
                Q(email__icontains=search)
            )

        return Response(CustomerSerializer(customers, many=True).data)

    # ============================
    # POST → create customer OR add address to existing customer
    # ============================
    def post(self, request, customer_id=None, address_id=None):
        if customer_id:
            # This is for adding addresses to existing customer
            return self.add_address(request, customer_id)
        else:
            # This is for new customer registration
            return self.register_customer(request)

    def register_customer(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Check mobile already exists
        if User.objects.filter(mobile_no=data["mobile_no"]).exists():
            return Response({"detail": "Mobile number already registered"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check email exists (optional)
        if data.get("email") and User.objects.filter(email=data["email"]).exists():
            return Response({"detail": "Email already registered"},
                            status=status.HTTP_400_BAD_REQUEST)

        customer = serializer.save()
        return Response(CustomerRegistrationSerializer(customer).data, status=status.HTTP_201_CREATED)

    def add_address(self, request, customer_id):
        try:
            customer = User.objects.get(user_id=customer_id, role='customer')
        except User.DoesNotExist:
            return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if we're setting as primary
        is_primary = request.data.get('is_primary', False)
        
        # If setting as primary, remove primary from existing addresses
        if is_primary:
            Address.objects.filter(user=customer, is_primary=True).update(is_primary=False)

        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create address with customer relationship
        address = Address.objects.create(user=customer, **serializer.validated_data)
        
        return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)

    # ============================
    # PUT → update customer OR update address
    # ============================
    def put(self, request, customer_id, address_id=None):
        if address_id:
            # This is for updating an address
            return self.update_address(request, customer_id, address_id)
        else:
            # This is for updating customer info
            return self.update_customer(request, customer_id)

    def update_customer(self, request, customer_id):
        try:
            customer = User.objects.get(user_id=customer_id, role="customer")
        except User.DoesNotExist:
            return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerRegistrationSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_address(self, request, customer_id, address_id):
        try:
            customer = User.objects.get(user_id=customer_id, role='customer')
            address = Address.objects.get(pk=address_id, user=customer)
        except (User.DoesNotExist, Address.DoesNotExist):
            return Response({"detail": "Customer or address not found"}, status=status.HTTP_404_NOT_FOUND)

        # Handle primary address logic
        is_primary = request.data.get('is_primary', False)
        current_is_primary = address.is_primary
        
        if is_primary and not current_is_primary:
            # Setting this address as primary
            Address.objects.filter(user=customer, is_primary=True).update(is_primary=False)
        elif not is_primary and current_is_primary:
            # Removing primary from this address - we need to set another as primary
            other_addresses = Address.objects.filter(user=customer).exclude(pk=address_id)
            if other_addresses.exists():
                # Set the first other address as primary
                other_address = other_addresses.first()
                other_address.is_primary = True
                other_address.save()

        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    # ============================
    # DELETE → delete customer OR delete address
    # ============================
    def delete(self, request, customer_id, address_id=None):
        if address_id:
            # This is for deleting an address
            return self.delete_address(request, customer_id, address_id)
        else:
            # This is for soft deleting a customer
            return self.delete_customer(request, customer_id)

    def delete_customer(self, request, customer_id):
        try:
            customer = User.objects.get(user_id=customer_id, role="customer")
        except User.DoesNotExist:
            return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # SOFT DELETE
        customer.status = "inactive"
        customer.is_active = False
        customer.save()

        return Response({"detail": "Customer marked as inactive"}, status=status.HTTP_200_OK)

    def delete_address(self, request, customer_id, address_id):
        try:
            customer = User.objects.get(user_id=customer_id, role='customer')
            address = Address.objects.get(pk=address_id, user=customer)
        except (User.DoesNotExist, Address.DoesNotExist):
            return Response({"detail": "Customer or address not found"}, status=status.HTTP_404_NOT_FOUND)

        # If deleting primary address, set another as primary
        if address.is_primary:
            other_addresses = Address.objects.filter(user=customer).exclude(pk=address_id)
            if other_addresses.exists():
                other_address = other_addresses.first()
                other_address.is_primary = True
                other_address.save()

        address.delete()
        return Response({"message": "Address deleted successfully"}, status=status.HTTP_200_OK)
    
    


# class CustomerAPIView(APIView):

#     # ============================
#     # GET  → list customers
#     # ============================
#     def get(self, request, customer_id=None):
#         search = request.query_params.get("search")

#         if customer_id:  
#             customer = get_object_or_404(User, user_id=customer_id, role="customer")

#             return Response(CustomerSerializer(customer).data)

#         customers = User.objects.filter(role="customer")

#         if search:
#             customers = customers.filter(
#                 Q(name__icontains=search) |
#                 Q(mobile_no__icontains=search) |
#                 Q(email__icontains=search)
#             )

#         return Response(CustomerSerializer(customers, many=True).data)

#     # ============================
#     # POST → create customer
#     # ============================
#     def post(self, request, customer_id=None):
#         if customer_id:
#             # This is for adding addresses to existing customer
#             return self.add_address(request, customer_id)
#         else:
#             # This is for new customer registration
#             return self.register_customer(request)
    
#     def register_customer(self, request):
#         serializer = CustomerRegistrationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data

#         # Check mobile already exists
#         if User.objects.filter(mobile_no=data["mobile_no"]).exists():
#             return Response({"detail": "Mobile number already registered"},
#                             status=status.HTTP_400_BAD_REQUEST)

#         # Check email exists (optional)
#         if data.get("email") and User.objects.filter(email=data["email"]).exists():
#             return Response({"detail": "Email already registered"},
#                             status=status.HTTP_400_BAD_REQUEST)

#         customer = serializer.save()
#         return Response(CustomerRegistrationSerializer(customer).data, status=status.HTTP_201_CREATED)
    
#     def add_address(self, request, customer_id):
#         try:
#             customer = User.objects.get(user_id=customer_id, role='customer')
#         except User.DoesNotExist:
#             return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = AddressSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         address = Address.objects.create(user=customer, **serializer.validated_data)
#         return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)
    
#     def put(self, request, customer_id):
#         try:
#             customer = User.objects.get(user_id=customer_id, role="customer")
#         except User.DoesNotExist:
#             return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = CustomerRegistrationSerializer(customer, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     # ============================
#     # DELETE → delete customer
#     # ============================
#     def delete(self, request, customer_id):
#         try:
#             customer = User.objects.get(user_id=customer_id, role="customer")
#         except User.DoesNotExist:
#             return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

#         # SOFT DELETE
        
#         customer.status = "inactive"
#         customer.save()

#         return Response({"detail": "Customer marked as inactive"}, status=status.HTTP_200_OK)



class CustomerOrderAPIView(APIView):

    # ============================
    # GET → fetch orders by customer_id
    # ============================
    def get(self, request, customer_id):
        customer = get_object_or_404(User, id=customer_id, role="customer")

        orders = Order.objects.filter(customer=customer).order_by("-created_at")

        # Optional Filters
        status_filter = request.query_params.get("status")
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")

        if status_filter:
            orders = orders.filter(status=status_filter)

        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)

        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)

        return Response(OrderSerializer(orders, many=True).data)

    # ============================
    # POST → create order for customer
    # ============================
    def post(self, request, customer_id):
        customer = get_object_or_404(User, id=customer_id, role="customer")

        data = request.data.copy()
        data["customer"] = customer.id

        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        return Response(OrderSerializer(order).data, status=201)

    # ============================
    # PUT → update order
    # ============================
    def put(self, request, customer_id):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response({"detail": "order_id is required"}, status=400)

        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_order = serializer.save()

        return Response(OrderSerializer(updated_order).data)

    # ============================
    # DELETE → cancel order
    # ============================
    def delete(self, request, customer_id):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response({"detail": "order_id is required"}, status=400)

        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

        # Soft delete = cancel order
        order.status = "cancelled"
        order.save()

        return Response({"message": "Order cancelled successfully"})


    # ============================
    # PUT → update customer
    # ============================
    def put(self, request, customer_id):
        customer = get_object_or_404(User, id=customer_id, role="customer")

        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_customer = serializer.save()

        return Response(CustomerSerializer(updated_customer).data)

    # ============================
    # DELETE → soft delete
    # ============================
    def delete(self, request, customer_id):
        customer = get_object_or_404(User, id=customer_id, role="customer")
        customer.status = "inactive"
        customer.save()

        return Response({"message": "Customer deleted successfully"})


class StaffView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # ============================
    # GET → staff / addresses
    # ============================
    
    
    def get(self, request, user_id=None, address_id=None):
        
        if user_id:
            staff = get_object_or_404(User, user_id=user_id, role="staff")

            if address_id:
                address = get_object_or_404(Address, pk=address_id, user=staff)
                return Response(AddressSerializer(address).data)

            addresses = Address.objects.filter(user=staff)
            return Response({
                "staff": StaffSerializer(staff).data,
                "addresses": AddressSerializer(addresses, many=True).data
            })

        staff_qs = User.objects.filter(role="staff")
        return Response(StaffSerializer(staff_qs, many=True).data)

    # ============================
    # POST → create staff / add address
    # ============================
    def post(self, request, user_id=None):
        if user_id:
            return self.add_address(request, user_id)
    
        data = request.data.copy()
        data["role"] = "staff"
    
       
        if not request.FILES.get("image"):
            data.pop("image", None)
    
        serializer = StaffSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
    
        
        if request.FILES.get("image"):
            staff.image = request.FILES["image"]
            staff.save()
    
        return Response(StaffSerializer(staff).data, status=201)


    def add_address(self, request, user_id):
        staff = get_object_or_404(User, user_id=user_id, role="staff")

        is_primary = request.data.get("is_primary", False)
        if is_primary:
            Address.objects.filter(user=staff, is_primary=True).update(is_primary=False)

        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address = Address.objects.create(
            user=staff,
            **serializer.validated_data
        )

        return Response(AddressSerializer(address).data, status=201)

    # ============================
    # PUT → update staff / address
    # ============================
    def put(self, request, user_id, address_id=None):
        if address_id:
            return self.update_address(request, user_id, address_id)
    
        staff = get_object_or_404(User, user_id=user_id, role="staff")
    
        data = request.data.copy()
    
        # Remove 'image' from data if no file was uploaded
        if not request.FILES.get("image"):
            data.pop("image", None)
    
        serializer = StaffSerializer(staff, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
    
        # Assign the image if uploaded
        if request.FILES.get("image"):
            staff.image = request.FILES["image"]
            staff.save()
    
        return Response(StaffSerializer(staff).data)


    def update_address(self, request, user_id, address_id):
        staff = get_object_or_404(User, user_id=user_id, role="staff")
        address = get_object_or_404(Address, pk=address_id, user=staff)

        is_primary = request.data.get("is_primary", False)

        if is_primary and not address.is_primary:
            Address.objects.filter(user=staff, is_primary=True).update(is_primary=False)
        elif not is_primary and address.is_primary:
            other = Address.objects.filter(user=staff).exclude(pk=address_id).first()
            if other:
                other.is_primary = True
                other.save()

        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # ============================
    # DELETE → staff / address
    # ============================
    def delete(self, request, user_id, address_id=None):
        if address_id:
            return self.delete_address(request, user_id, address_id)

        staff = get_object_or_404(User, user_id=user_id, role="staff")
        staff.status = "inactive"
        staff.is_active = False
        staff.save()

        return Response({"detail": "Staff marked as inactive"}, status=200)

    def delete_address(self, request, user_id, address_id):
        staff = get_object_or_404(User, user_id=user_id, role="staff")
        address = get_object_or_404(Address, pk=address_id, user=staff)

        if address.is_primary:
            other = Address.objects.filter(user=staff).exclude(pk=address_id).first()
            if other:
                other.is_primary = True
                other.save()

        address.delete()
        return Response({"detail": "Address deleted successfully"}, status=200)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Order, OrderItem, Address, User
from .serializers import OrderSerializer, OrderItemSerializer
from .utils import (
    convert_order_status,
    convert_service_type,
    convert_category_name,
    convert_product_name,
    generate_token,
    get_created_by_identifier,
)


    

    # -----------------------------------------
    # GET Orders
    # -----------------------------------------


class StaffOrderView(APIView):

    def get(self, request, user_id):
        staff = get_object_or_404(User, user_id=user_id, role="staff")
        staff_name = staff.name

        # Booked orders: orders created/assigned by this staff
        booked_orders = Order.objects.filter(user_id=staff.user_id).order_by("-created_at")

        # Picked orders: staff has picked
        picked_orders = Order.objects.filter(
            picked_by=staff_name,
            status=Order.OrderStatus.PICKED
        ).order_by("-picked_at")

        # Delivered orders: staff has delivered
        delivered_orders = Order.objects.filter(
            delivered_by=staff_name,
            status=Order.OrderStatus.DELIVERED
        ).order_by("-delivered_at")

        data = {
            "booked_orders": OrderSerializer(booked_orders, many=True).data,
            "picked_orders": OrderSerializer(picked_orders, many=True).data,
            "delivered_orders": OrderSerializer(delivered_orders, many=True).data
        }

        return Response(data, status=status.HTTP_200_OK)


    # -----------------------------------------
    # POST: Create a new order
    # -----------------------------------------
    def post(self, request):
        data = request.data
        staff_user = request.user

        try:
            # Handle customer assignment
            customer_id = data.get("customer_id")
            if customer_id:
                customer = get_object_or_404(User, pk=customer_id)
            else:
                customer = staff_user

            # Handle address creation
            address_data = data.get("address", {})
            address = Address.objects.create(
                user=customer,
                name=customer.name,
                mobile_no=customer.mobile_no,
                address_line1=address_data.get("address_line1"),
                address_line2=address_data.get("address_line2"),
                city=address_data.get("city"),
                pincode=address_data.get("pincode"),
                landmark=address_data.get("landmark", ""),
            )

            # Create Order
            token_no = generate_token()
            created_by = get_created_by_identifier(staff_user, data)
            service_type = convert_service_type(data.get("service"))

            order = Order.objects.create(
                user=customer,
                address=address,
                Token_no=token_no,
                service=service_type,
                status=Order.Status.PENDING,
                created_by=created_by,
                updated_by=created_by,
            )

            # Create Order Items
            items_data = data.get("items", [])
            for item in items_data:
                OrderItem.objects.create(
                    order=order,
                    category_name=item.get("category_name"),
                    product_name=item.get("product_name"),
                    quantity=item.get("quantity"),
                    service=service_type,
                    status="pending",
                    created_by=created_by,
                    updated_by=created_by,
                )

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Staff order creation failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # -----------------------------------------
    # PUT: Update order
    # -----------------------------------------
    def put(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        data = request.data
        staff_user = request.user
        identifier = staff_user.mobile_no or staff_user.email or staff_user.name
        now = timezone.now()

        # Update status
        if "status" in data:
            new_status = convert_order_status(data["status"])
            order.status = new_status

            # Automatically update timestamps and who did the action
            if new_status == Order.Status.PICKED_UP:
                order.picked_at = now
                order.picked_by = identifier
            elif new_status == Order.Status.COMPLETED:
                order.delivered_at = now
                order.delivered_by = identifier
            elif new_status == Order.Status.CANCELLED:
                order.cancelled_at = now
                order.cancelled_by = identifier

      
        if "service" in data:
            order.service = convert_service_type(data["service"])

       
        address_fields = ["address_line1", "address_line2", "city", "state", "pincode", "landmark"]
        if any(field in data for field in address_fields):
            address = order.address
            for field in address_fields:
                if field in data:
                    setattr(address, field, data[field])
            address.save()

        order.updated_at = now
        order.updated_by = identifier
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # -----------------------------------------
    # DELETE: Delete order
    # -----------------------------------------
    def delete(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.utils import timezone

from .models import Order
from .serializers import OrderSerializer,WebsiteOrderSerializer,WebsiteAddressSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import IntegrityError

from .models import Order
from .serializers import OrderSerializer


class OrderActionView(APIView):

    def post(self, request, order_id, action):
        # ✅ IMPORTANT: use order_id field
        order = get_object_or_404(Order, order_id=order_id)

        staff_user = request.user
        staff_identifier = getattr(staff_user, "user_id", None)
        now = timezone.now()

        if not staff_identifier:
            return Response(
                {"detail": "Invalid staff user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # ------------------------------
            # CONFIRM
            # ------------------------------
            if action == "confirm":
                order.status = Order.OrderStatus.CONFIRMED
                order.confirmed_at = now
                order.updated_by = staff_identifier

            # ------------------------------
            # PICK
            # ------------------------------
            elif action == "pick":
                order.status = Order.OrderStatus.PICKED
            
                entered_token = request.data.get("token_no")
            
                if entered_token:
                  
                    if Order.objects.filter(
                        Token_no=entered_token
                    ).exclude(
                        order_id=order.order_id
                    ).exclude(
                        status=Order.OrderStatus.DELIVERED
                    ).exists():
                        return Response(
                            {"detail": "Token already exists."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
                    order.Token_no = entered_token
                else:
                    if not order.Token_no:
                        order.Token_no = Order.generate_token()
            
                order.picked_at = now
                order.picked_by = staff_identifier
                order.updated_by = staff_identifier


            # ------------------------------
            # DELIVER
            # ------------------------------
            elif action == "deliver":
                order.status = Order.OrderStatus.DELIVERED
                order.delivered_at = now
                order.delivered_by = staff_identifier
                order.updated_by = staff_identifier

            else:
                return Response(
                    {"detail": "Invalid action"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response(
                {"detail": "Database error: Token may already exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"detail": f"Failed to process order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceView(APIView):

    authentication_classes = []   
    permission_classes = []     
    def get(self, request, service_id=None):
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            serializer = ServiceSerializer(service)
            return Response(serializer.data)
        else:
            services = Service.objects.all()
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)

    def put(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(ServiceSerializer(service).data)

    def delete(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        service.delete()
        return Response({"detail": "Service deleted"},status=status.HTTP_204_NO_CONTENT)
    


# ---------------------------------------------------------
# CATEGORY VIEW (FULL NESTED SUPPORT)
# ---------------------------------------------------------
class CategoryView(APIView):
    authentication_classes = []    # <— ANYONE CAN ACCESS
    permission_classes = []     
    def get(self, request, service_id=None, category_id=None):
        # -----------------------------------------
        # /services/<service_id>/categories/
        # -----------------------------------------
        if service_id and category_id is None:
            categories = ServiceCategory.objects.filter(service_id=service_id)
            serializer = ServiceCategorySerializer(categories, many=True)
            return Response(serializer.data)

        # -----------------------------------------
        # /services/<service_id>/categories/<category_id>
        # -----------------------------------------
        if service_id and category_id:
            category = get_object_or_404(
                ServiceCategory, id=category_id, service_id=service_id
            )
            serializer = ServiceCategorySerializer(category)
            return Response(serializer.data)

        # -----------------------------------------
        # /categories/
        # -----------------------------------------
        if category_id is None:
            categories = ServiceCategory.objects.all()
            serializer = ServiceCategorySerializer(categories, many=True)
            return Response(serializer.data)

        # -----------------------------------------
        # /categories/<category_id>
        # -----------------------------------------
        category = get_object_or_404(ServiceCategory, id=category_id)
        serializer = ServiceCategorySerializer(category)
        return Response(serializer.data)
    
    def post(self, request, service_id=None):
        data = request.data.copy()

        # -----------------------------------------
        # 1️⃣ If service_id is provided (nested)
        # -----------------------------------------
        if service_id is not None:
            service = get_object_or_404(Service, id=service_id)
            data['service'] = service.id

        # -----------------------------------------
        # 2️⃣ If service_id is NOT provided,
        #    use 'service' field from request body (if exists)
        # -----------------------------------------
        else:
            if 'service' not in data:
                return Response(
                    {"error": "service is required (either via URL or body)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ServiceCategorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(
            ServiceCategorySerializer(category).data,
            status=status.HTTP_201_CREATED
        )


    def put(self, request, category_id):
        category = get_object_or_404(ServiceCategory, id=category_id)
        serializer = ServiceCategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(ServiceCategorySerializer(category).data)

    def delete(self, request, category_id):
        category = get_object_or_404(ServiceCategory, id=category_id)
        category.delete()
        return Response({"detail": "Category deleted"}, status=status.HTTP_204_NO_CONTENT)


 
# --------------------------
# Product Views
# --------------------------

# ---------------------------------------------------------
# PRODUCT VIEW (FULL NESTED SUPPORT)
# ---------------------------------------------------------
class ProductView(APIView):
    authentication_classes = []    
    permission_classes = []     
    def get(self, request, service_id=None, category_id=None, product_id=None):

        # ---------------------------------------------------
        # /services/<service_id>/categories/<category_id>/products
        # ---------------------------------------------------
        if service_id and category_id and not product_id:
            products = ServiceProduct.objects.filter(category_id=category_id)
            serializer = ServiceProductSerializer(products, many=True)
            return Response(serializer.data)

        # ---------------------------------------------------
        # /categories/<category_id>/products
        # ---------------------------------------------------
        if category_id and not product_id and not service_id:
            products = ServiceProduct.objects.filter(category_id=category_id)
            serializer = ServiceProductSerializer(products, many=True)
            return Response(serializer.data)

        # ---------------------------------------------------
        # /services/<service_id>/categories/<category_id>/products/<product_id>
        # ---------------------------------------------------
        if service_id and category_id and product_id:
            product = get_object_or_404(ServiceProduct, id=product_id, category_id=category_id)
            serializer = ServiceProductSerializer(product)
            return Response(serializer.data)

        # ---------------------------------------------------
        # /categories/<category_id>/products/<product_id>
        # ---------------------------------------------------
        if category_id and product_id:
            product = get_object_or_404(ServiceProduct, id=product_id, category_id=category_id)
            serializer = ServiceProductSerializer(product)
            return Response(serializer.data)

        # ---------------------------------------------------
        # /products/
        # ---------------------------------------------------
        if product_id is None:
            products = ServiceProduct.objects.all()
            serializer = ServiceProductSerializer(products, many=True)
            return Response(serializer.data)

        # ---------------------------------------------------
        # /products/<product_id>
        # ---------------------------------------------------
        product = get_object_or_404(ServiceProduct, id=product_id)
        serializer = ServiceProductSerializer(product)
        return Response(serializer.data)

    def post(self, request, category_id=None, service_id=None):
        data = request.data.copy()

        # ----------------------------------------------------
        # 1️⃣ If category_id is provided via URL
        # ----------------------------------------------------
        if category_id is not None:
            category = get_object_or_404(ServiceCategory, id=category_id)

            # If service_id is also given, validate relationship
            if service_id is not None and category.service_id != service_id:
                return Response(
                    {"error": "Category does not belong to the given service."},
                    status=400
                )

            data['category'] = category.id

        else:
            # ----------------------------------------------------
            # 2️⃣ No category_id in URL — require "category" in body
            # ----------------------------------------------------
            if 'category' not in data:
                return Response(
                    {"error": "category is required (either via URL or body)."},
                    status=400
                )

            # Validate the category exists
            category = get_object_or_404(ServiceCategory, id=data['category'])

        # ----------------------------------------------------
        # 3️⃣ Create the product
        # ----------------------------------------------------
        serializer = ServiceProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response(
            ServiceProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, product_id):
        product = get_object_or_404(ServiceProduct, id=product_id)
        serializer = ServiceProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ServiceProductSerializer(product).data)

    def delete(self, request, product_id):
        product = get_object_or_404(ServiceProduct, id=product_id)
        product.delete()
        return Response({"detail": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)


class ServiceFullDetailsView(APIView):
   
    permission_classes = [AllowAny]
    # ----------------------------------------
    # GET → ALL SERVICES WITH FULL NESTED DATA
    # ----------------------------------------
    def get(self, request, service_id=None):
        if service_id is None:
            services = Service.objects.all()
            data = self.serialize_service_list(services)
            return Response(data, status=200)
        
        service = get_object_or_404(Service, id=service_id)
        data = self.serialize_service(service)
        return Response(data, status=200)

    # -------------------------------------
    # POST → CREATE SERVICE + CATEGORIES + PRODUCTS
    # Body Example:
    # {
    #   "name": "Laundry",
    #   "categories": [
    #       {
    #         "name": "Men",
    #         "products": [
    #             {"name": "Shirt", "price": 25},
    #             {"name": "Pant", "price": 30}
    #         ]
    #       }
    #   ]
    # }
    # -------------------------------------
    def post(self, request):
        data = request.data

        # Create Service
        service = Service.objects.create(name=data["name"])

        # Create nested categories + products
        for cat in data.get("categories", []):
            category = ServiceCategory.objects.create(
                name=cat["name"],
                service=service
            )

            for prod in cat.get("products", []):
                ServiceProduct.objects.create(
                    name=prod["name"],
                    price=prod["price"],
                    category=category
                )

        return Response(self.serialize_service(service), status=201)

    # -------------------------------------
    # PUT → UPDATE SERVICE + CATEGORIES + PRODUCTS
    # -------------------------------------
    def put(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        data = request.data

        # Update service
        service.name = data.get("name", service.name)
        service.save()

        # Delete old categories & products → easier handling
        ServiceCategory.objects.filter(service=service).delete()

        # Recreate tree
        for cat in data.get("categories", []):
            category = ServiceCategory.objects.create(
                name=cat["name"],
                service=service
            )

            for prod in cat.get("products", []):
                ServiceProduct.objects.create(
                    name=prod["name"],
                    price=prod["price"],
                    category=category
                )

        return Response(self.serialize_service(service), status=200)

    # -------------------------------------
    # DELETE → DELETE SERVICE + NESTED DATA
    # -------------------------------------
    def delete(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        service.delete()
        return Response({"message": "Service & all nested data deleted"}, status=204)

    # -------------------------------------
    # HELPER: SERIALIZE SINGLE SERVICE
    # -------------------------------------
    def serialize_service(self, service):
        categories = ServiceCategory.objects.filter(service=service)

        return {
            "id": service.id,
            "name": service.name,
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "products": [
                        {
                            "id": prod.id,
                            "name": prod.name,
                            "price": prod.price
                        }
                        for prod in ServiceProduct.objects.filter(category=cat)
                    ]
                }
                for cat in categories
            ]
        }

    # -------------------------------------
    # HELPER: SERIALIZE LIST OF SERVICES
    # -------------------------------------
    def serialize_service_list(self, services):
        return [self.serialize_service(s) for s in services]


class OrderItemView(APIView):

    def get(self, request, order_id, item_id=None):
        if item_id:
            item = get_object_or_404(OrderItem, order_id=order_id, order_item_id=item_id)
            return Response(OrderItemSerializer(item).data)

        items = OrderItem.objects.filter(order_id=order_id)
        return Response(OrderItemSerializer(items, many=True).data)

    def post(self, request, order_id):
        data = request.data
        many = isinstance(data, list)

        serializer = OrderItemSerializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)

        created_items = []

        for item in serializer.validated_data if many else [serializer.validated_data]:
            obj, _ = OrderItem.objects.update_or_create(
                order_id=order_id,
                product=item["product"],
                service=item["service"],
                defaults={
                    "category": item["category"],
                    "quantity": item.get("quantity", 1),
                    "status": item.get("status", "pending"),
                }
            )
            created_items.append(obj)

        return Response(
            OrderItemSerializer(created_items, many=True).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, order_id, item_id):
        item = get_object_or_404(OrderItem, order_id=order_id, order_item_id=item_id)
        serializer = OrderItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderItemSerializer(item).data)

    def delete(self, request, order_id, item_id):
        item = get_object_or_404(OrderItem, order_id=order_id, order_item_id=item_id)
        item.delete()
        return Response({"success": True}, status=204)


import traceback


# class OrderView(APIView):
    

#     def get(self, request, order_id=None, user_id=None):
#         if order_id:
#             order = get_object_or_404(Order, order_id=order_id)

#             serializer = OrderSerializer(order)
#         else:
#             if user_id:
#                 orders = Order.objects.filter(user_id=user_id)
#             else:
#                 orders = Order.objects.all()
#             serializer = OrderSerializer(orders, many=True)
#         return Response(serializer.data)

    
    

#     def post(self, request, user_id=None):
#         try:
#             print("📦 Received order data:", request.data)

#             # Extract user_id from payload
#             payload_user_id = request.data.get('user_id')
#             if not payload_user_id:
#                 return Response(
#                     {"detail": "user_id is required in the request body"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Permission check
#             current_user = request.user
#             if current_user.role == "customer" and current_user.user_id != payload_user_id:
#                 return Response(
#                     {"detail": "Customers can only create orders for themselves"},
#                     status=status.HTTP_403_FORBIDDEN
#                 )

#             # Ensure target user exists
#             try:
#                 target_user = User.objects.get(user_id=payload_user_id)
#             except User.DoesNotExist:
#                 return Response(
#                     {"detail": f"User with user_id {payload_user_id} does not exist"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Validate main order data
#             serializer = OrderSerializer(data=request.data)
            
#             serializer.is_valid(raise_exception=True)

#             # Role-based initial status
#             initial_status = "pending"
#             if current_user.role in ["admin"]:
#                 initial_status = "confirmed"

#             # FIX: Remove incoming status to prevent duplicate keyword argument
#             validated = serializer.validated_data.copy()
#             validated.pop("status", None)

#             # ---- CREATE ORDER ----
#             order = Order.objects.create(
#                 user_id=payload_user_id,
#                 status=initial_status,
#                 **validated
#             )

#             print("✅ Order created successfully:", order.order_id,)

#             # ---- CREATE ORDER ITEMS ----
#             items_data = request.data.get('items', [])
#             print(f"📋 Processing {len(items_data)} items...")

#             order_items = []

#             for item_data in items_data:
#                 try:
#                     print(f"🔍 Item: {item_data}")

#                     # Service lookup
#                     service_id = item_data.get("service_id") or item_data.get("service")
#                     if not service_id:
#                         raise ValueError("service_id is required in each item")

#                     service = Service.objects.get(id=service_id)

#                     # Category & Product
#                     category_name = item_data.get('category_name')
#                     product_name = item_data.get('product_name')

#                     if not category_name or not product_name:
#                         raise ValueError("category_name and product_name required")

#                     # Category ensure exists
#                     category, created = ServiceCategory.objects.get_or_create(
#                         name=category_name,
#                         defaults={"description": f"Auto-created category {category_name}"}
#                     )
#                     if created:
#                         print(f"🆕 Created new category: {category.name}")

#                     # Product ensure exists
#                     product, created = ServiceProduct.objects.get_or_create(
#                         name=product_name,
#                         defaults={
#                             "category": category,
#                             "price": item_data.get("price", 0),
#                             "description": f"Auto-created product {product_name}"
#                         }
#                     )
#                     if created:
#                         print(f"🆕 Created new product: {product.name}")

#                     # Create OrderItem
#                     oi = OrderItem.objects.create(
#                         order=order,
#                         service=service,
#                         category=category,
#                         product=product,
#                         quantity=item_data.get("quantity", 1)
#                     )

#                     order_items.append(oi)
#                     print(f"✅ Added item: {product.name} x{oi.quantity}")

#                 except Exception as item_error:
#                     print(f"❌ Error creating item: {item_error}")
#                     print(traceback.format_exc())

#             # Debug count
#             db_item_count = OrderItem.objects.filter(order=order).count()
#             print(f"📌 DB item count: {db_item_count}")

#             # Prepare final response
#             order.refresh_from_db()
#             response_serializer = OrderSerializer(order)

#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             print("❌ Error creating order:", str(e))
#             print(traceback.format_exc())
#             return Response(
#                 {"detail": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


#     def put(self, request, order_id):
#         print(f"🔄 PUT request received for order {order_id}")
#         print(f"📦 Request data: {request.data}")
        
#         order = get_object_or_404(Order, order_id=order_id)
        
#         # Update order fields
#         serializer = OrderSerializer(order, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
        
#         # Handle order items update if provided
#         if 'items' in request.data and isinstance(request.data['items'], list):
#             items_data = request.data['items']
#             print(f"📋 Processing {len(items_data)} order items for update...")
            
#             for item_data in items_data:
#                 order_item_id = item_data.get('order_item_id')
#                 if order_item_id:
#                     try:
#                         # Update existing order item
#                         order_item = OrderItem.objects.get(
#                             order_item_id=order_item_id, 
#                             order=order
#                         )
                        
#                         # Update quantity
#                         if 'quantity' in item_data:
#                             order_item.quantity = item_data['quantity']
                        
#                         # Update service if provided
#                         if 'service' in item_data:
#                             try:
#                                 service = Service.objects.get(name=item_data['service'])
#                                 order_item.service = service
#                             except Service.DoesNotExist:
#                                 print(f"⚠️ Service '{item_data['service']}' not found")
                        
#                         # Update status if provided
#                         if 'status' in item_data:
#                             order_item.status = item_data['status']
                        
#                         order_item.save()
#                         print(f"✅ Updated order item {order_item_id}: quantity={order_item.quantity}")
                        
#                     except OrderItem.DoesNotExist:
#                         print(f"⚠️ Order item {order_item_id} not found for order {order_id}")
#                         # Create new item if needed
#                         if all(k in item_data for k in ['category_name', 'product_name']):
#                             print(f"➕ Creating new order item...")
#                             # Similar logic to post method
#                             try:
#                                 service = Service.objects.get(name=item_data.get('service', order.service))
#                                 category = ServiceCategory.objects.get(name=item_data['category_name'])
#                                 product = ServiceProduct.objects.get(name=item_data['product_name'])
                                
#                                 OrderItem.objects.create(
#                                     order=order,
#                                     service=service,
#                                     category=category,
#                                     product=product,
#                                     quantity=item_data.get('quantity', 1),
#                                     status=item_data.get('status', 'pending')
#                                 )
#                                 print(f"✅ Created new order item")
#                             except Exception as e:
#                                 print(f"❌ Error creating order item: {e}")
        
#         # Refresh order to get updated items
#         order.refresh_from_db()
        
#         # Return updated order with items
#         response_serializer = OrderSerializer(order)
#         print(f"✅ Order {order_id} updated successfully")
#         return Response(response_serializer.data)

#     def delete(self, request, order_id):
#         order = get_object_or_404(Order, order_id=order_id)
#         order.delete()
#         return Response({"success": True, "message": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, Service, ServiceCategory, ServiceProduct
from .serializers import OrderSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from decimal import Decimal
from django.db.models import Sum
from .models import Order, OrderItem, Service, ServiceCategory, ServiceProduct
from .serializers import OrderSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Order, OrderItem, Service, ServiceCategory, ServiceProduct
from .serializers import OrderSerializer

class OrderView(APIView):

    # =========================
    # GET ORDER(S)
    # =========================
    def get(self, request, order_id=None, user_id=None):
        if order_id:
            order = get_object_or_404(Order, order_id=order_id)
            return Response(OrderSerializer(order).data)

        orders = Order.objects.filter(user_id=user_id) if user_id else Order.objects.all()
        return Response(OrderSerializer(orders, many=True).data)

    # =========================
    # CREATE ORDER
    # =========================
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            user=serializer.validated_data["user"],
            address=serializer.validated_data["address"],
            service=serializer.validated_data["service"],
            status="confirmed" if getattr(request.user, "role", None) == "admin" else "pending",
            created_by=str(request.user),
        )

        self._handle_items(order, request.data.get("items", []))
        order.refresh_from_db()

        return Response(OrderSerializer(order).data, status=201)

    # =========================
    # UPDATE ORDER
    # =========================
    def put(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self._handle_items(order, request.data.get("items", []))
        order.refresh_from_db()

        return Response(OrderSerializer(order).data)

    # =========================
    # DELETE ORDER
    # =========================
    def delete(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        order.delete()
        return Response({"success": True}, status=204)

    # =========================
    # HANDLE ORDER ITEMS
    # =========================
    def _handle_items(self, order, items_data):
        """
        Accept only the items you send.
        Clears previous items before creating new ones.
        Ensures price and total_price are correctly calculated.
        """
        # Remove old items
        OrderItem.objects.filter(order=order).delete()

        bulk_items = []
        for item in items_data:
            service = self._get_service(item)
            category = self._get_category(item, service)
            product = self._get_product(item, category)

            quantity = int(item.get("quantity", 1))
            price = Decimal(item.get("price") or product.price or 0)
            total_price = price * quantity

            bulk_items.append(
                OrderItem(
                    order=order,
                    service=service,
                    category=category,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total_price=total_price,
                    status=item.get("status", "pending"),
                )
            )

        OrderItem.objects.bulk_create(bulk_items)

    # =========================
    # HELPERS: SERVICE / CATEGORY / PRODUCT
    # =========================
    def _get_service(self, item):
        value = item.get("service") or item.get("service_id")
        if not value:
            raise ValidationError("Service is required")

        # Try integer first
        service = None
        try:
            service_id = int(value)
            service = Service.objects.filter(id=service_id).first()
        except (ValueError, TypeError):
            service = Service.objects.filter(name__iexact=str(value).strip()).first()

        if not service:
            raise ValidationError(f"Service '{value}' not found")
        return service

    def _get_category(self, item, service):
        value = item.get("category_name") or item.get("category_id")
        if not value:
            raise ValidationError("Category is required")

        category = None
        try:
            category_id = int(value)
            category = ServiceCategory.objects.filter(id=category_id, service=service).first()
        except (ValueError, TypeError):
            category = ServiceCategory.objects.filter(name__iexact=str(value).strip(), service=service).first()

        if not category:
            raise ValidationError(f"Category '{value}' not found for service '{service.name}'")
        return category

    def _get_product(self, item, category):
        value = item.get("product_name") or item.get("product_id")
        if not value:
            raise ValidationError("Product is required")

        product = None
        try:
            product_id = int(value)
            product = ServiceProduct.objects.filter(id=product_id, category=category).first()
        except (ValueError, TypeError):
            product = ServiceProduct.objects.filter(name__iexact=str(value).strip(), category=category).first()

        if not product:
            raise ValidationError(f"Product '{value}' not found in category '{category.name}'")
        return product


class PickupDeliveryView(APIView):
    
    def get(self, request, pd_id=None, order_id=None):
        if pd_id:
            pickup = get_object_or_404(PickupDelivery, id=pd_id)
            serializer = PickupDeliverySerializer(pickup)
            return Response(serializer.data)
        elif order_id:
            pickups = PickupDelivery.objects.filter(order_id=order_id)
            serializer = PickupDeliverySerializer(pickups, many=True)
            return Response(serializer.data)
        else:
            pickups = PickupDelivery.objects.all()
            serializer = PickupDeliverySerializer(pickups, many=True)
            return Response(serializer.data)


    def post(self, request):
        serializer = PickupDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pickup = PickupDelivery.objects.create(**serializer.validated_data)
        return Response(PickupDeliverySerializer(pickup).data, status=status.HTTP_201_CREATED)

    def put(self, request, pd_id):
        pickup = get_object_or_404(PickupDelivery, id=pd_id)
        serializer = PickupDeliverySerializer(pickup, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_data = serializer.validated_data

        now = timezone.now()

        # Handle automatic timestamps based on status changes
        if 'status' in update_data:
            new_status = update_data['status']

            if new_status == PickupDelivery.ServiceType.PICKUP and not pickup.picked_at:
                update_data['picked_at'] = now

            elif new_status == PickupDelivery.ServiceType.DELIVERY and not pickup.delivered_at:
                update_data['delivered_at'] = now

            # Set actual_date if status updated
            update_data['actual_date'] = now

        # Apply updates to the instance
        for field, value in update_data.items():
            setattr(pickup, field, value)

        pickup.updated_at = now
        pickup.save()

        return Response(PickupDeliverySerializer(pickup).data)

    def delete(self, request, pd_id):
        pickup = get_object_or_404(PickupDelivery, id=pd_id)
        pickup.delete()
        return Response({"success": True, "message": "Pickup/Delivery deleted"})
    


from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class PickupDeliveryActionView(APIView):
    """
    POST /pickup-delivery/{pd_id}/{action}/
    action: mark-picked-up / mark-delivered
    """
    def post(self, request, pd_id, action):
        pickup = get_object_or_404(PickupDelivery, id=pd_id)
        now = timezone.now()

        if action == "mark-picked-up" and pickup.service_type == PickupDelivery.ServiceType.PICKUP:
            pickup.picked_at = now
            pickup.status = PickupDelivery.ServiceType.PICKUP
        elif action == "mark-delivered" and pickup.service_type == PickupDelivery.ServiceType.DELIVERY:
            pickup.delivered_at = now
            pickup.status = PickupDelivery.ServiceType.DELIVERY
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        pickup.actual_date = now
        pickup.save()

        from .serializers import PickupDeliverySerializer
        return Response(PickupDeliverySerializer(pickup).data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Feedback, Order, User
from .serializers import FeedbackSerializer
from .permissions import IsStaffOrAdmin

class FeedbackView(APIView):

    # -----------------------------------------
    # GET
    # -----------------------------------------
    def get(self, request, feedback_id=None, order_id=None, user_id=None):

        # Get single feedback by ID
        if feedback_id:
            feedback = get_object_or_404(Feedback, pk=feedback_id)
            serializer = FeedbackSerializer(feedback)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get feedback(s) by order
        if order_id:
            feedbacks = Feedback.objects.filter(order_id=order_id).order_by('-pk')
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get feedbacks by user
        if user_id:
            feedbacks = Feedback.objects.filter(user_id=user_id).order_by('-pk')
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get all feedbacks
        feedbacks = Feedback.objects.all().order_by('-pk')
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # -----------------------------------------
    # POST
    # -----------------------------------------
    def post(self, request, order_id=None):
        data = request.data
        user = request.user

        # Force add order id in payload
        data["order"] = order_id

        # Validate ratings between 1 and 5
        ratings = [
            data.get("rating"),
            data.get("service_quality", 5),
            data.get("delivery_time", 5),
            data.get("staff_behavior", 5),
        ]

        for rating in ratings:
            if rating is None or rating < 1 or rating > 5:
                return Response(
                    {"detail": "All ratings must be between 1 and 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------
    # PUT
    # -----------------------------------------
    def put(self, request, feedback_id):
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        user = request.user

        # Only owner or staff/admin can update
        if feedback.user != user and user.role not in ["staff", "admin"]:
            raise PermissionDenied("Not authorized to update this feedback")

        serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
        if serializer.is_valid():

            # Block normal user from editing reply
            if user.role not in ["staff", "admin"] and "reply" in serializer.validated_data:
                serializer.validated_data.pop("reply")

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------
    # DELETE
    # -----------------------------------------
    def delete(self, request, feedback_id):
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        user = request.user

        # Only owner can delete
        if feedback.user != user:
            raise PermissionDenied("Not authorized to delete this feedback")

        feedback.delete()
        return Response({"message": "Feedback deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

from .models import Order  # make sure this path is correct


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # -----------------------------
        # 1. Read filters from request
        # -----------------------------
        status_filter = request.GET.get("status", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        orders = Order.objects.all()

        # -----------------------------
        # 2. Apply STATUS filter
        # -----------------------------
        if status_filter:
            orders = orders.filter(status=status_filter)

        # -----------------------------
        # 3. Apply DATE filter
        # -----------------------------
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                orders = orders.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                orders = orders.filter(created_at__date__lte=end_date)

        # -----------------------------
        # 4. Calculations
        # -----------------------------

        total_orders = orders.count()

        # order counts by status
        pending_orders = orders.filter(status="pending").count()
        confirmed_orders = orders.filter(status="confirmed").count()
        picked_up_orders = orders.filter(status="picked_up").count()
        ready_to_pick_orders = orders.filter(status="ready_to_pick").count()
        in_progress_orders = orders.filter(status="in_progress").count()
        completed_orders = orders.filter(status="completed").count()
        delivered_orders = orders.filter(status="delivered").count()
        cancelled_orders = orders.filter(status="cancelled").count()
        rejected_orders = orders.filter(status="rejected").count()

        # custom calculation example
        ready_to_pick_calculated = (
            confirmed_orders + in_progress_orders - picked_up_orders
        )
        if ready_to_pick_calculated < 0:
            ready_to_pick_calculated = 0

        today = datetime.now().date()
        today_orders = orders.filter(created_at__date=today).count()

        # -----------------------------
        # 5. Response
        # -----------------------------
        return Response({
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "picked_up_orders": picked_up_orders,
            "ready_to_pick_orders": ready_to_pick_orders,
            "ready_to_pick_calculated": ready_to_pick_calculated,
            "completed_orders": completed_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "rejected_orders": rejected_orders,
            "today_orders": today_orders,
        })


from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order


class MonthlyOrdersReportView(APIView):

    def get(self, request):
        queryset = (
            Order.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_orders=Count('order_id'))
            .order_by('month')
        )

        data = [
            {
                "month": item["month"].strftime("%Y-%m"),
                "total_orders": item["total_orders"]
            }
            for item in queryset
        ]

        return Response({
            "status": True,
            "data": data
        })
        
        


from .models import User, Address, Order, OrderItem, Service, ServiceCategory, ServiceProduct
from .serializers import WebsiteOrderSerializer, WebsiteAddressSerializer,WebsiteIndividualAddressSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import traceback

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import traceback
import sys
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import sys, traceback

from .models import (
    User, Address, Service,
    ServiceCategory, ServiceProduct,
    Order, OrderItem
)
from .serializers import WebsiteOrderSerializer


class WebsiteOrderView(APIView):
    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data

            # -----------------------------
            # 1. BASIC VALIDATION
            # -----------------------------
            required_fields = [
                "customer_name",
                "customer_mobile",
                "address_line1",
                "city",
                "pincode",
                "service_id",
                "items"
            ]

            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return Response(
                    {"error": "Missing required fields", "fields": missing},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(str(data["pincode"])) != 6:
                return Response(
                    {"error": "Pincode must be exactly 6 digits"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(data["items"], list) or not data["items"]:
                return Response(
                    {"error": "Items must be a non-empty list"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # -----------------------------
            # 2. USER
            # -----------------------------
            user, _ = User.objects.get_or_create(
                mobile_no=data["customer_mobile"],
                defaults={
                    "name": data["customer_name"],
                    "role": "customer",
                    "is_active": True
                }
            )

            # -----------------------------
            # 3. ADDRESS
            # -----------------------------
            address = Address.objects.create(
                user=user,
                address_line1=data["address_line1"],
                address_line2=data.get("address_line2", ""),
                landmark=data.get("landmark", ""),
                city=data["city"],
                pincode=data["pincode"],
                address_type="home",
                is_primary=True
            )

            # -----------------------------
            # 4. SERVICE
            # -----------------------------
            try:
                order_service = Service.objects.get(id=data["service_id"])
            except Service.DoesNotExist:
                return Response(
                    {"error": f"Service ID {data['service_id']} not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # -----------------------------
            # 5. ORDER (FIXED)
            # -----------------------------
            order = Order.objects.create(
                user=user,
                address=address,
                service=order_service,
                status=Order.OrderStatus.PENDING,
                created_by="Customer",
                updated_by="Customer"
            )

            # -----------------------------
            # 6. ORDER ITEMS
            # -----------------------------
            for index, item in enumerate(data["items"], start=1):
                try:
                    OrderItem.objects.create(
                        order=order,
                        service=Service.objects.get(id=item["service_id"]),
                        category=ServiceCategory.objects.get(id=item["category_id"]),
                        product=ServiceProduct.objects.get(id=item["product_id"]),
                        quantity=int(item.get("quantity", 1)),
                        status=OrderItem.OrderItemStatus.PENDING
                    )
                except KeyError as e:
                    return Response(
                        {"error": f"Item {index} missing field {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Exception as e:
                    raise Exception(f"Item {index} error → {str(e)}")

            # -----------------------------
            # 7. RESPONSE
            # -----------------------------
            serializer = WebsiteOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # -----------------------------
        # DEBUG 500 (TEMP ONLY)
        # -----------------------------
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            return Response(
                {
                    "DEBUG_500": True,
                    "error_type": exc_type.__name__,
                    "error_message": str(e),
                    "file": exc_tb.tb_frame.f_code.co_filename if exc_tb else None,
                    "line": exc_tb.tb_lineno if exc_tb else None,
                    "traceback": traceback.format_exc()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
            
class OrderDashboardCounts(APIView):

    def get(self, request):
        timeline = request.GET.get('timeline', 'all_time')
        status_filter = request.GET.get('status')

        qs = Order.objects.all()

        # -----------------------------
        # ⏱️ TIMELINE FILTERS
        # -----------------------------
        today = now().date()

        if timeline == 'today':
            qs = qs.filter(created_at__date=today)

        elif timeline == 'this_week':
            start_week = today - timedelta(days=today.weekday())
            qs = qs.filter(created_at__date__gte=start_week)

        elif timeline == 'this_month':
            qs = qs.filter(
                created_at__year=today.year,
                created_at__month=today.month
            )

        elif timeline == 'this_year':
            qs = qs.filter(created_at__year=today.year)

        elif timeline == 'specific_date':
            date = request.GET.get('date')
            if date:
                qs = qs.filter(created_at__date=date)

        elif timeline == 'date_range':
            from_date = request.GET.get('from')
            to_date = request.GET.get('to')
            if from_date and to_date:
                qs = qs.filter(
                    created_at__date__gte=from_date,
                    created_at__date__lte=to_date
                )

        # -----------------------------
        # 📊 STATUS COUNTS (BASE)
        # -----------------------------
        data = qs.aggregate(
            pending=Count('pk', filter=Q(status='pending')),
            confirmed_total=Count(
                'pk',
                filter=Q(status__in=['confirmed', 'picked', 'delivered', 'cancelled'])
            ),
            ready_to_pick=Count('pk', filter=Q(status='confirmed')),
            picked=Count('pk', filter=Q(status='picked')),
            delivered=Count('pk', filter=Q(status='delivered')),
            cancelled=Count('pk', filter=Q(status='cancelled')),
            rejected=Count('pk', filter=Q(status='rejected')),
            total=Count('pk')
        )

        # -----------------------------
        # 🎯 STATUS FILTER (OPTIONAL)
        # -----------------------------
        if status_filter:
            status_map = {
                'pending': Q(status='pending'),
                'confirmed_total': Q(status__in=['confirmed', 'picked', 'delivered', 'cancelled']),
                'ready_to_pick': Q(status='confirmed'),
                'picked': Q(status='picked'),
                'delivered': Q(status='delivered'),
                'cancelled': Q(status='cancelled'),
                'rejected': Q(status='rejected'),
            }

            if status_filter in status_map:
                data = {
                    'status': status_filter,
                    'count': qs.filter(status_map[status_filter]).count()
                }

        return Response(data)



import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Order, OrderItem
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Order, OrderItem
from django.conf import settings

import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Order, OrderItem
from django.conf import settings
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Order, OrderItem
from django.conf import settings
from PIL import Image, ImageOps
from reportlab.lib.utils import ImageReader
import os
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Sum
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Order, OrderItem

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Sum
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Order, OrderItem


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Sum
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Order, OrderItem

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Sum
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Order, OrderItem


class OrderReceiptDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id):

        order = get_object_or_404(Order, order_id=order_id)
        items = OrderItem.objects.filter(order=order)

        # =========================
        # HTTP RESPONSE
        # =========================
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="order_{order.order_id}_receipt.pdf"'
        )

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # =========================
        # CONSTANTS
        # =========================
        LEFT = 20 * mm
        RIGHT = width - 20 * mm
        TOP = height - 20 * mm
        BOTTOM = 30 * mm
        FOOTER_START_Y = BOTTOM + 60
        ROW_HEIGHT = 22

        # Columns
        COL_SERVICE = LEFT
        COL_CATEGORY = LEFT + 120
        COL_PRODUCT = LEFT + 240
        COL_QTY = LEFT + 360
        COL_PRICE = LEFT + 420

        # =========================
        # HEADER
        # =========================
        def draw_header():
            y = TOP
            p.setFont("Helvetica", 9)
            p.drawString(LEFT, y, "GSTIN: 33BYRPR9662M2ZA")
            p.drawRightString(RIGHT, y, "Cell: 9003 600 601")

            logo = os.path.join(settings.BASE_DIR, "laundryapp/static/images/Logo 1.png")
            if os.path.exists(logo):
                p.drawImage(logo, LEFT, y - 90, 80, 80, mask="auto")

            iso = os.path.join(settings.BASE_DIR, "laundryapp/static/images/ISO.jpg")
            if os.path.exists(iso):
                p.drawImage(iso, RIGHT - 80, y - 90, 80, 80, mask="auto")

            p.setFont("Helvetica-Bold", 18)
            p.drawCentredString(width / 2, y - 20, "SMART WASH LAUNDRY")
            p.setFont("Helvetica-Bold", 11)
            p.drawCentredString(width / 2, y - 38, "(Premium Laundry Services)")

            p.setFont("Helvetica", 9)
            address_lines = [
                "10/11, 5 - L.Vaithilinga Nadar Complex",
                "Keelasurandai",
                "Surandai - 627859",
            ]
            ay = y - 55
            for line in address_lines:
                p.drawCentredString(width / 2, ay, line)
                ay -= 12

            p.line(LEFT, ay - 5, RIGHT, ay - 5)
            return ay - 20

        # =========================
        # CUSTOMER DETAILS
        # =========================
        def draw_customer_details(y):
            p.setFont("Helvetica", 10)
            line_gap = 14
            left_x = LEFT
            right_x = width / 2 + 20
        
           
            customer_name = order.user.name if order.user else "N/A"
            customer_mobile = order.user.mobile_no if order.user else "N/A"
        
           
            p.drawString(left_x, y, f"Customer Name : {customer_name}")
            p.drawString(left_x, y - line_gap, f"Mobile        : {customer_mobile}")
            p.drawString(left_x, y - (2 * line_gap), f"Order ID      : {order.order_id}")
            p.drawString(
                left_x,
                y - (3 * line_gap),
                f"Order Date    : {order.created_at.strftime('%d-%m-%Y') if order.created_at else ''}",
            )
        
            
            addr = getattr(order, "address", None)
            if addr:
                line1 = getattr(addr, "address_line1", "")
                line2 = getattr(addr, "address_line2", "")
                city = getattr(addr, "city", "")
                pincode = getattr(addr, "pincode", "")
            else:
                line1 = line2 = city = pincode = ""
        
            p.drawString(right_x, y, "Address:")
            p.drawString(right_x, y - line_gap, line1)
            p.drawString(right_x, y - (2 * line_gap), line2)
            p.drawString(right_x, y - (3 * line_gap), f"{city} - {pincode}")
        
            p.line(LEFT, y - (4 * line_gap) - 5, RIGHT, y - (4 * line_gap) - 5)
            return y - (4 * line_gap) - 20

        # =========================
        # TABLE HEADER
        # =========================
        def draw_table_header(y):
            p.setFont("Helvetica-Bold", 11)
            p.rect(LEFT, y - ROW_HEIGHT, RIGHT - LEFT, ROW_HEIGHT)
            p.line(COL_CATEGORY - 10, y, COL_CATEGORY - 10, y - ROW_HEIGHT)
            p.line(COL_PRODUCT - 10, y, COL_PRODUCT - 10, y - ROW_HEIGHT)
            p.line(COL_QTY - 10, y, COL_QTY - 10, y - ROW_HEIGHT)
            p.line(COL_PRICE - 10, y, COL_PRICE - 10, y - ROW_HEIGHT)

            p.drawString(COL_SERVICE + 5, y - 15, "Service")
            p.drawString(COL_CATEGORY + 5, y - 15, "Category")
            p.drawString(COL_PRODUCT + 5, y - 15, "Product")
            p.drawRightString(COL_QTY + 30, y - 15, "Qty")
            p.drawRightString(COL_PRICE + 30, y - 15, "Price")
            return y - ROW_HEIGHT

        # =========================
        # FOOTER
        # =========================
        def draw_footer():
            footer_y = FOOTER_START_Y + 30

            # ---------------- Separator line ----------------
            p.line(LEFT, footer_y + 25, RIGHT, footer_y + 25)

            # ================= LEFT =================
    
            p.setFont("Helvetica", 10)

            # Base Y position for the top line
            base_y = footer_y + 8

            # Define equal line spacing
            line_spacing = 14  # adjust this to make space between lines

            # Draw the lines with equal spacing
            p.drawString(LEFT, base_y, "SmartWashLaundrySurandai")
            p.drawString(LEFT, base_y - line_spacing, "www.smartwashlaundrysurandai.in")
            p.drawString(LEFT, base_y - (2 * line_spacing), "mobile_no : 6385600601")

            # ================= CENTER (SHIFTED RIGHT) =================
            CENTER_OFFSET = 20  # <<< tweak this value if needed
            center_x = (width / 2) + CENTER_OFFSET

            whatsapp_img = os.path.join(
                settings.BASE_DIR, "laundryapp/static/images/whatsapp.png"
            )

            # ---- Center title ----
            title_text = "DOOR STEP PICKUP & DELIVERY"
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(center_x, footer_y + 6, title_text)

            # ---- WhatsApp icon + mobile number ----
            mobile_text = "9003 600 601"
            p.setFont("Helvetica-Bold", 10)
            mobile_text_width = p.stringWidth(mobile_text, "Helvetica-Bold", 10)

            icon_size = 14
            gap = 5
            group_width = icon_size + gap + mobile_text_width
            start_x = center_x - (group_width / 2)

            if os.path.exists(whatsapp_img):
                p.drawImage(
                    whatsapp_img,
                    start_x,
                    footer_y - 14,
                    icon_size,
                    icon_size,
                    mask="auto",
                )

            p.drawString(
                start_x + icon_size + gap,
                footer_y - 12,
                mobile_text,
            )

            # ================= RIGHT =================
            truck = os.path.join(
                settings.BASE_DIR, "laundryapp/static/images/delivery.png"
            )

            if os.path.exists(truck):
                p.drawImage(
                    truck,
                    RIGHT - 70,
                    footer_y - 6,
                    70,
                    30,
                    mask="auto",
                )

        # =========================
        # SAFE AMOUNT FUNCTION
        # =========================
        def safe_amount(val):
            return float(val) if val else 0.0

        # =========================
        # START DRAWING
        # =========================
        y = draw_header()
        y = draw_customer_details(y)
        y = draw_table_header(y)
        p.setFont("Helvetica", 10)

        for item in items:
            if y < FOOTER_START_Y + 50:
                draw_footer()
                p.showPage()
                y = draw_header()
                y = draw_customer_details(y)
                y = draw_table_header(y)
                p.setFont("Helvetica", 10)
        
            p.rect(LEFT, y - ROW_HEIGHT, RIGHT - LEFT, ROW_HEIGHT)
            p.line(COL_CATEGORY - 10, y, COL_CATEGORY - 10, y - ROW_HEIGHT)
            p.line(COL_PRODUCT - 10, y, COL_PRODUCT - 10, y - ROW_HEIGHT)
            p.line(COL_QTY - 10, y, COL_QTY - 10, y - ROW_HEIGHT)
            p.line(COL_PRICE - 10, y, COL_PRICE - 10, y - ROW_HEIGHT)
        
            p.drawString(COL_SERVICE + 5, y - 15, str(item.service.name))
            p.drawString(COL_CATEGORY + 5, y - 15, str(item.category.name))
            p.drawString(COL_PRODUCT + 5, y - 15, str(item.product.name))
            p.drawRightString(COL_QTY + 30, y - 15, str(item.quantity))
            p.drawRightString(COL_PRICE + 30, y - 15, f"{safe_amount(item.total_price):.2f}")
            y -= ROW_HEIGHT

        # TOTAL
        total = items.aggregate(total=Sum("total_price")).get("total")
        total = safe_amount(total)
        if y < FOOTER_START_Y + 50:
            draw_footer()
            p.showPage()
            y = draw_header()
            y = draw_customer_details(y)
            y = draw_table_header(y)
        p.setFont("Helvetica-Bold", 11)
        p.drawRightString(COL_PRICE + 30, y - 15, f"Total : {total:.2f}")

        
        draw_footer()
        p.showPage()
        p.save()

        return response
