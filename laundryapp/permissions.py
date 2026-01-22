# laundryapp/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUserOnly(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsStaffUser(BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'staff'


class IsCustomerUser(BasePermission):
    """
    Allows access only to customer users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True
        # Write permissions only for the owner
        return obj.user == request.user


class IsStaffOrAdmin(BasePermission):
    """
    Allows access to staff or admin users only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['staff', 'admin']
