from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class ProfileAdmin(UserAdmin):
    pass
