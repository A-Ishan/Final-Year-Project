from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'verification_status')
    list_filter = ('verification_status',)
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)
