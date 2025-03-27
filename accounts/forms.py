from django import forms
from .models import User, PhoneOTP
from .models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    retype_password = forms.CharField(widget=forms.PasswordInput, label="Retype Password")

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        retype_password = cleaned_data.get("retype_password")
        if password != retype_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LoginForm(forms.Form):
    login_field = forms.CharField(label="Username or Phone Number")
    password = forms.CharField(widget=forms.PasswordInput)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")

class VerificationStatusForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['verification_status', 'rejection_reason']

class KYCForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'social_media_link', 'verification_reason','kyc_document_front', 'kyc_document_back', 'kyc_document_selfie']


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']