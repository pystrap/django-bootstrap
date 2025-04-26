from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppSettings, User


class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ('name',)
    search_fields = ['name', 'data']


admin.site.register(AppSettings, AppSettingsAdmin)


class CustomUserAdmin(UserAdmin):
    # Define custom fields to display and edit
    fieldsets = UserAdmin.fieldsets + (
        ('User', {'fields': ('last_seen', 'need_reset_password')}),  # Add your custom fields here
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'email', 'is_model',)}),  # Add your custom fields for user creation
    )


admin.site.register(User, CustomUserAdmin)
