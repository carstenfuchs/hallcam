"""Admin Configuration for Improved User"""

# As recommended in the documentation [1], this file is a customized copy of
# the `admin.py` file that ships with the Improved User package.
# [1] https://django-improved-user.readthedocs.io/en/latest/admin_usage.html

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from improved_user.forms import UserChangeForm, UserCreationForm

from Accounts.models import User


class CustomUserAdmin(UserAdmin):
    """Admin panel for Improved User, mimics Django's default"""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "short_name")}),
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
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "short_name", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("email", "full_name", "short_name", "is_staff", "is_superuser", "is_active")
    readonly_fields = ("last_login", "date_joined")
    search_fields = ("email", "full_name", "short_name")
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)
