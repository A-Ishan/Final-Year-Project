from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('normal', 'Normal User'),
        ('admin', 'Admin User'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal')
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    admin_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
