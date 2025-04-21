from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Core API endpoints
    path('api/v1/', include('core.urls')),
    
    # Django AllAuth URLs (if needed)
    path('accounts/', include('allauth.urls')),
]

# Custom admin site settings
admin.site.site_header = 'Cloud Manager Admin'
admin.site.site_title = 'Cloud Manager Admin Portal'
admin.site.index_title = 'Welcome to Cloud Manager Admin Portal'
