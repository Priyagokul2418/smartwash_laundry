from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return JsonResponse({
        "status": True,
        "message": "SmartWash Laundry API is running",
        "version": "v1"
    })

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/v1/", include("laundryapp.urls")),
]


# If you want MEDIA served by Django (not recommended for heavy prod traffic),
# keep this enabled even in prod. Otherwise configure Apache to serve /media/.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



