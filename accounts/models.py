from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None):
        if not username:
            raise ValueError("The Username field is required")
        if not phone_number:
            raise ValueError("The Phone Number field is required")
        user = self.model(username=username, phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None):
        user = self.create_user(username, phone_number, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_phone_verified = True  # Superuser phone is auto-verified
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^(98|97)\d{8}$', message="Phone number must be 10 digits starting with 98 (Nepal).")
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
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

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.username
    
class PhoneOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.otp} for {self.user.phone_number}"