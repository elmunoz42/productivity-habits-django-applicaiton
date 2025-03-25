# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model to allow for additional fields and customization.
    """
    bio = models.TextField(_("Bio"), blank=True)
    timezone = models.CharField(_("Timezone"), max_length=50, blank=True)
    daily_reminder_time = models.TimeField(_("Daily Reminder Time"), null=True, blank=True)
    weekly_reminder_day = models.IntegerField(
        _("Weekly Reminder Day"),
        choices=[(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 
                                                  'Thursday', 'Friday', 'Saturday', 'Sunday'])],
        null=True,
        blank=True
    )
    weekly_reminder_time = models.TimeField(_("Weekly Reminder Time"), null=True, blank=True)
    quarterly_reminder_enabled = models.BooleanField(_("Quarterly Reminder Enabled"), default=True)
    
    def __str__(self):
        return self.username

# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the CustomUser model.
    """
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "bio")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Reminders"), {"fields": ("timezone", "daily_reminder_time", "weekly_reminder_day", 
                                    "weekly_reminder_time", "quarterly_reminder_enabled")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration with custom fields.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'timezone')
        
class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating user information.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'timezone',
                  'daily_reminder_time', 'weekly_reminder_day', 'weekly_reminder_time',
                  'quarterly_reminder_enabled')

# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'