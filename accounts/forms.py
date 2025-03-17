from django import forms
from .models import CustomUser

class VerificationStatusForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['verification_status', 'rejection_reason']

class KYCForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'social_media_link', 'verification_reason','kyc_document_front', 'kyc_document_back', 'kyc_document_selfie']


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
