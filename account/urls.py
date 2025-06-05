# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,ProfileViewSet,SendOTPView,VerifyOTPAndResetPasswordView,UserListViewSet,CommentListCreateView,CommentRetrieveUpdateDestroyView


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
# router.register(r'login', LoginViewSet, basename='login')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'user-list', UserListViewSet, basename='user-list')

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('reset-password/', VerifyOTPAndResetPasswordView.as_view(), name='reset-password'),
     path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
     path('comments/<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
    
]
