# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from .forms import AdminUserCreationForm, CustomUserChangeForm

class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ('access_code',)
    autocomplete_fields = ('parent',)

class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
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

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent', 'access_code', 'phone_number', 'date_of_birth')
    list_filter = ('parent',)
    readonly_fields = ('access_code',)
    search_fields = ('user__username', 'user__email', 'access_code', 'parent__username', 'parent__email')
    autocomplete_fields = ('parent',)
