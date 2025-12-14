from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
  fieldsets = UserAdmin.fieldsets + (
    (None, {'fields': ('user_type',)}),
  )

  list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active','stripe_customer_id')

admin.site.register(CustomUser, CustomUserAdmin)