from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # New fields for KYC verification
    
    full_name = models.CharField(max_length=255, blank=True, null=True)
    social_media_link = models.URLField(blank=True, null=True)
    
    verification_reason = models.TextField(blank=True, null=True)
    kyc_document_front = models.ImageField(upload_to='kyc_documents/', null=True, blank=True)
    kyc_document_back = models.ImageField(upload_to='kyc_documents/', null=True, blank=True)
    kyc_document_selfie = models.ImageField(upload_to='kyc_documents/', null=True, blank=True)
    kyc_verified = models.BooleanField(default=False)  # This is to track if the user is verified

    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        null=True, 
        blank=True
    )
    STATUS_CHOICES = [
        ('pending', 'Documents Sent for Verification'),
        ('verified', 'Your Document has been Verified'),
        ('rejected', 'Verification Rejected'),
        ('kyc_required', 'Please Proceed to KYC Verification'),
    ]
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='kyc_required')
    rejection_reason = models.TextField(blank=True, null=True)

    # Fix clashes by adding related_name arguments
    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions", blank=True
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username
