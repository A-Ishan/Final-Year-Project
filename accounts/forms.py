# forms.py

from django import forms
from .models import CustomUser

class KYCForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['kyc_document_front', 'kyc_document_back', 'kyc_document_selfie']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kyc_document_front'].required = True
        self.fields['kyc_document_back'].required = True
        self.fields['kyc_document_selfie'].required = True
