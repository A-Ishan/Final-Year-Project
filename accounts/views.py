import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser

otp_storage = {}  # Temporary storage for OTPs

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp  # Store OTP temporarily

    send_mail(
        "Your OTP Code",
        f"Your OTP is: {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return otp

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        send_otp(email)
        request.session["signup_data"] = {"username": username, "email": email, "password": password}
        return redirect("verify_otp")

    return render(request, "accounts/signup.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.session["signup_data"]["email"]
        entered_otp = request.POST["otp"]

        if otp_storage.get(email) == entered_otp:
            data = request.session.pop("signup_data")
            user = CustomUser.objects.create_user(username=data["username"], email=data["email"], password=data["password"])
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP.")
            return redirect("verify_otp")

    return render(request, "accounts/verify_otp.html")

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username_or_email, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")
