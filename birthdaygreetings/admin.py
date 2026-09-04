# Register your models here.

# birthdaygreetings/admin.py
from django import forms
from django.contrib import admin, messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from .models import BirthdayProfile


class BirthdayProfileAdminForm(forms.ModelForm):
    class Meta:
        model = BirthdayProfile
        fields = '__all__'
        help_texts = {
            'custom_message': 'Optional special greeting. Use the emoji toolbar below the field to add 🎉🎂🎈 and more.',
        }

    class Media:
        css = {'all': ('birthdaygreetings/emoji_picker.css',)}
        js = ('birthdaygreetings/emoji_picker.js',)

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            return user
        qs = BirthdayProfile.objects.filter(user=user)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This user already has a birthday profile.')
        return user


@admin.register(BirthdayProfile)
class BirthdayProfileAdmin(admin.ModelAdmin):
    form = BirthdayProfileAdminForm
    list_display = ('user', 'role', 'date_of_birth', 'grade_or_department', 'is_birthday_today')
    list_filter = ('role', 'date_of_birth')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'grade_or_department')
    actions = ('delete_selected_immediately',)

    def has_module_permission(self, request):
        role = str(getattr(request.user, 'role', '')).upper()
        return request.user.is_superuser or request.user.is_staff or role == 'ADMIN'

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

    @admin.action(description='Delete selected birthday profiles immediately')
    def delete_selected_immediately(self, request, queryset):
        selected_count = queryset.count()
        if not selected_count:
            self.message_user(request, 'No birthday profiles selected.', level=messages.WARNING)
            return
        try:
            queryset.delete()
            self.message_user(request, f'{selected_count} birthday profile(s) deleted successfully.', level=messages.SUCCESS)
        except IntegrityError:
            self.message_user(
                request,
                'Bulk delete failed due to related records. Remove dependent records first and retry.',
                level=messages.ERROR,
            )

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def get_queryset(self, request):
        # Use an inner join to avoid rendering rows with stale user references.
        return super().get_queryset(request).select_related('user').filter(user__isnull=False)

    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request, extra_context=extra_context)
        except IntegrityError:
            self.message_user(
                request,
                'Birthday profiles could not be listed due to invalid related user data. Please refresh and try again.',
                level=messages.ERROR,
            )
            return HttpResponseRedirect(request.path)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except IntegrityError:
            self.message_user(
                request,
                'Save failed because the selected user record is invalid or was removed. Please select an active existing user and try again.',
                level=messages.ERROR,
            )
            return HttpResponseRedirect(request.path)

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except IntegrityError:
            self.message_user(
                request,
                'Delete failed due to related records. Remove dependent records first and retry.',
                level=messages.ERROR,
            )

    def delete_queryset(self, request, queryset):
        try:
            super().delete_queryset(request, queryset)
        except IntegrityError:
            self.message_user(
                request,
                'Bulk delete failed due to related records. Remove dependent records first and retry.',
                level=messages.ERROR,
            )