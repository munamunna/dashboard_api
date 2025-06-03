# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager 

class CustomUser(AbstractUser):
    
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

