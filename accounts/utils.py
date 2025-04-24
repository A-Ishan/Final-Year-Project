import random
import requests
from django.conf import settings

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def send_otp(phone_number, otp):
    url = "https://sms.aakashsms.com/sms/v3/send/"
    payload = {
        'auth_token': settings.AAKASH_SMS_TOKEN,  # Add your token from the dashboard
        'to': phone_number,
        'text': f'Your OTP is {otp}. Valid for 5 minutes.',
    }
    
    response = requests.post(url, data=payload)
    return response.status_code == 200
