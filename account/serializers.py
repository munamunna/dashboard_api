
from rest_framework import serializers
from django.contrib.auth import get_user_model
import string
import random
from django.contrib.auth import authenticate


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





User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # authenticate requires username param, but your USERNAME_FIELD is email
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Both "email" and "password" are required.')

        attrs['user'] = user
        return attrs
