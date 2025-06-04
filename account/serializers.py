
from rest_framework import serializers
from django.contrib.auth import get_user_model
import string
import random
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        # Auto-generate strong password if not provided
        password = validated_data.get('password') or self.generate_strong_password()
        user = User(email=validated_data['email'])
        user.set_password(password)
        user.save()

        # Optionally attach the password to response context
        self.context['generated_password'] = password
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'generated_password' in self.context:
            data['generated_password'] = self.context['generated_password']
        return data

    def generate_strong_password(self, length=12):
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+[]{}|;:,.<>?"
        return ''.join(random.choice(chars) for _ in range(length))







from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser  # Your custom user model

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD  # Use 'email' for authentication

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")

        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'role': user.role,
        }

        return data




# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             # authenticate requires username param, but your USERNAME_FIELD is email
#             user = authenticate(request=self.context.get('request'), username=email, password=password)
#             if not user:
#                 raise serializers.ValidationError('Invalid email or password.')
#             if not user.is_active:
#                 raise serializers.ValidationError('User account is disabled.')
#         else:
#             raise serializers.ValidationError('Both "email" and "password" are required.')

#         attrs['user'] = user
#         return attrs





class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'address', 'profile_picture']

class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)

        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
