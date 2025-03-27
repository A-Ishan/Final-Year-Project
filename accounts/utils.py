import random
import requests
from django.conf import settings

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def send_otp(phone_number, otp):
    url = "http://api.sparrowsms.com/v2/sms/"
    payload = {
        'token': settings.SPARROW_SMS_TOKEN,
        'from': settings.SPARROW_SMS_FROM,
        'to': phone_number,
        'text': f'Your OTP is {otp}. Valid for 5 minutes.',
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200