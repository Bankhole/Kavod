# Register your models here.

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'is_important', 'is_published', 'author', 'created_at')
    list_filter = ('target_audience', 'is_important', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_important', 'is_published')
    exclude = ('author',)
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

    @admin.action(description='Delete selected announcements immediately')
    def delete_selected_immediately(self, request, queryset):
        selected_count = queryset.count()
        if not selected_count:
            self.message_user(request, 'No announcements selected.', level=messages.WARNING)
            return
        try:
            queryset.delete()
            self.message_user(request, f'{selected_count} announcement(s) deleted successfully.', level=messages.SUCCESS)
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

    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request, extra_context=extra_context)
        except IntegrityError:
            self.message_user(
                request,
                'Announcement update failed because of invalid related user data. Please refresh and try again.',
                level=messages.ERROR,
            )
            return HttpResponseRedirect(request.path)

    def save_model(self, request, obj, form, change):
        User = get_user_model()
        if request.user.is_authenticated and User.objects.filter(pk=request.user.pk).exists():
            obj.author = request.user
        else:
            obj.author = None

        try:
            super().save_model(request, obj, form, change)
        except IntegrityError:
            # If a stale user FK caused this save to fail, clear author and retry once.
            obj.author = None
            super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        return super().changeform_view(request, object_id, form_url, extra_context)

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