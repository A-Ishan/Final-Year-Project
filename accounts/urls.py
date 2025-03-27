from django.urls import path, include

from .views import signup_view, verify_otp_view, login_view, logout_view, kyc_verification, update_profile_picture
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('verify-otp/<int:user_id>/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('account/verify/', kyc_verification, name='kyc_verification'),
    path("update-profile-picture/", update_profile_picture, name="update_profile_picture"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)