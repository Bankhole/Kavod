# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ('access_code',)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_form_template = 'admin/change_form.html'
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('School Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'role', 'password1', 'password2'),
            },
        ),
    )
    inlines = [ProfileInline]

admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_code', 'phone_number', 'date_of_birth')
    readonly_fields = ('access_code',)
    search_fields = ('user__username', 'user__email', 'access_code')
