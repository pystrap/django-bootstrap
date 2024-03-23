from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppSettings, User


class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ('name',)
    search_fields = ['name', 'data']


admin.site.register(AppSettings, AppSettingsAdmin)


class CustomUserAdmin(UserAdmin):
    # Add custom admin configuration here
    pass


admin.site.register(User, CustomUserAdmin)
