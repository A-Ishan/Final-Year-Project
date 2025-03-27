from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm, OTPForm
from .models import User, PhoneOTP
from .utils import generate_otp, send_otp
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import User
from datetime import timedelta
from .forms import KYCForm, VerificationStatusForm, ProfilePictureForm
import requests

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Generate and send OTP
            otp = generate_otp()
            PhoneOTP.objects.create(user=user, otp=otp)
            if send_otp(user.phone_number, otp):
                messages.success(request, "OTP sent to your phone.")
                return redirect('verify_otp', user_id=user.id)
            else:
                messages.error(request, "Failed to send OTP.")
                user.delete()  # Rollback if OTP fails
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def verify_otp_view(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            otp_obj = PhoneOTP.objects.filter(user=user, otp=otp_input, is_used=False).first()
            if otp_obj and (timezone.now() - otp_obj.created_at) < timedelta(minutes=5):
                otp_obj.is_used = True
                otp_obj.save()
                user.is_phone_verified = True
                user.save()
                messages.success(request, "Phone verified successfully. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPForm()
    return render(request, 'accounts/verify_otp.html', {'form': form, 'user_id': user_id})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_field = form.cleaned_data['login_field']
            password = form.cleaned_data['password']
            user = authenticate(request, username=login_field, password=password)
            if user and user.is_phone_verified:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('home')
            elif user and not user.is_phone_verified:
                messages.error(request, "Please verify your phone number first.")
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

@login_required
def kyc_verification(request):
    user = request.user

    if user.verification_status == 'verified':
        return render(request, 'accounts/verify.html', {
            'is_verified': True,
            'message': 'Your KYC has been successfully verified.',
        })
    
    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            user.verification_status = 'pending'  # Mark as pending after submission
            user.save()
            messages.success(request, "Documents uploaded successfully. Your verification is in process.")
            return redirect('kyc_verification')
    else:
        form = KYCForm(instance=user)

    return render(request, 'accounts/verify.html', {
        'form': form,
        'is_verified': False,
        'status': user.get_verification_status_display(),
        'rejection_reason': user.rejection_reason if user.verification_status == 'rejected' else None
    })

@login_required
def update_verification_status(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = VerificationStatusForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Verification status updated for {user_profile.username}.")
            return redirect('admin_dashboard')  # Redirect to admin page

    else:
        form = VerificationStatusForm(instance=user_profile)

    return render(request, 'accounts/update_verification_status.html', {'form': form, 'user_profile': user_profile})

@login_required
def update_profile_picture(request):
    user = request.user

    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("kyc_verification")  # Redirect back to the profile page

    else:
        form = ProfilePictureForm(instance=user)

    return render(request, "accounts/update_profile.html", {"form": form})