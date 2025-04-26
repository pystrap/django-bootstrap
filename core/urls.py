from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from utils.viewsets import AdminToolsViewSet, AccountViewSet
from .viewsets import LoginViewSet, RefreshViewSet, ChangePasswordView, UserViewSet

router = routers.SimpleRouter()
# AUTHENTICATION
router.register(r'user', UserViewSet, basename='user')
router.register(r'auth/login', LoginViewSet, basename='auth-login')
router.register(r'auth/refresh', RefreshViewSet, basename='auth-refresh')
router.register(r'account', AccountViewSet, basename='account')
# router.register(r'auth/change_password', ChangePasswordView.as_view(), basename='auth-change-password')

# utils
router.register(r'admin_tools', AdminToolsViewSet, basename='admin_tools')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailer.urls')),
    path('api/', include(router.urls)),
    path('api/auth/change_password/', ChangePasswordView.as_view()),
    path('api/auth/password_reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset')),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
