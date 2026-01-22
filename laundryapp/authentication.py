# authentication.py (new file create pannu)
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class NoCSRFAuthentication(JWTAuthentication):
    """JWT authentication without CSRF"""
    def enforce_csrf(self, request):
        return  # CSRF skip pannu