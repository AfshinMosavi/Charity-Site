from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import phone_validator
"""
An AbstractBaseUser model is a base class that should be added to build a custom authentication system.
the User model is a model that is ready and can be used without the need for an implementation.
"""

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('MF','Unset'),
    ]
    
    address = models.TextField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=2, choices = GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=15, validators=[phone_validator], blank=True, null=True)

    def __str__(self):
        if self.username == 'admin' and  self.is_staff == True:
            return f'◘{self.username}◘'
        return self.username

    @property
    def is_benefactor(self):
        return hasattr(self, 'benefactor')
    
    @property
    def is_charity(self):
        return hasattr(self, 'charity')











