import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from .forms import KYCForm, ProfilePictureForm

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
    user_profile = get_object_or_404(CustomUser, id=user_id)

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