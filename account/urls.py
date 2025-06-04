# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,ProfileViewSet,SendOTPView,VerifyOTPAndResetPasswordView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
# router.register(r'login', LoginViewSet, basename='login')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('reset-password/', VerifyOTPAndResetPasswordView.as_view(), name='reset-password'),
]
