from django.shortcuts import render
from rest_framework import viewsets, status,permissions
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer,CustomUserSerializer
import secrets
import string
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model





User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

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



from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

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




class ProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

