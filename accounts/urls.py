from django.urls import path, include

from .views import signup_view, verify_otp_view, login_view, logout_view, kyc_verification, update_profile_picture, verify_dashboard, verify_user,forgot_password_request_view, reset_password_otp_view, set_new_password_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('verify-otp/<int:user_id>/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('account/verify/', kyc_verification, name='kyc_verification'),
    path("update-profile-picture/", update_profile_picture, name="update_profile_picture"),
    path('accounts/verify/<int:user_id>/', verify_dashboard, name='verify_dashboard'),
    path('verify-kyc/<int:user_id>/', verify_user, name='verify_kyc'),
    path('forgot-password/', forgot_password_request_view, name='forgot_password'),
    path('reset-password-otp/<int:user_id>/', reset_password_otp_view, name='reset_password_otp'),
    path('set-new-password/<int:user_id>/', set_new_password_view, name='set_new_password'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)