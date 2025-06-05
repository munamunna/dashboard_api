from django.shortcuts import render
from rest_framework import viewsets, status,permissions,generics
from rest_framework.response import Response
from .models import CustomUser,Comment
from .serializers import UserSerializer,CustomUserSerializer,UserListSerializer,CommentSerializer
import secrets
import string
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.views import APIView
import random
from datetime import timedelta

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated











User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['post'] 

    def generate_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Auto-generate password if not provided
        if 'password' not in data or not data['password']:
            password = self.generate_password()
            data['password'] = password
            auto_generated = True
        else:
            password = data['password']
            auto_generated = False

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(password)
        user.save()

        response_data = {
            "message": "User created successfully",
            "result": True,
            "data": {
                "id": user.id,
                "email": user.email,
                
                "generated_password": password if auto_generated else "Provided by user"
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)





class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# class LoginViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.none()  # no need for queryset on login
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]
#     http_method_names = ['post']

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']

#         # Return minimal user info
#         return Response({
#             'id': user.id,
#             'email': user.email,
#             'role':user.role,
#             'message': 'Login successful'
#         }, status=status.HTTP_200_OK)








class UserListViewSet(viewsets.ViewSet):
    def list(self, request):
        users = CustomUser.objects.select_related('profile').all()
        serializer = UserListSerializer(users, many=True)
        return Response({
            "message": "User list fetched successfully",
            "result": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user




class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # send email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                'munapm1@gmail.com',#for development testing.
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)




class VerifyOTPAndResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user = CustomUser.objects.get(email=email)

            if user.otp != otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > user.otp_created_at + timedelta(minutes=10):
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.otp = None
            user.otp_created_at = None
            user.save()

            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)






class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Comment list fetched successfully',
            'result': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response({
            'message': 'Comment created successfully',
            'result': True,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)



class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "result": True,
            "data": serializer.data,
            "message": "Comment retrieved successfully"
        }, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.author:
            return Response({
                "result": False,
                "data": None,
                "message": "You cannot edit others' comments"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "result": True,
            "data": serializer.data,
            "message": "Comment updated successfully"
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.author:
            return Response({
                "result": False,
                "data": None,
                "message": "You cannot delete others' comments"
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({
            "result": True,
            "data": None,
            "message": "Comment deleted successfully"
        }, status=status.HTTP_200_OK)

