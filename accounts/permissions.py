"""Shared permission helpers driven by Django Groups assigned in the admin panel.

Group membership (not the self-reported `role` field) is the source of truth for
gating access to staff/teacher-only functionality, since `role` can be chosen by
users at registration and must never grant elevated access on its own.
"""
from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

ADMIN_GROUP = 'Admin'
TEACHER_GROUP = 'Teacher'
STUDENT_GROUP = 'Student'
PARENT_GROUP = 'Parent'

ALL_GROUPS = [ADMIN_GROUP, TEACHER_GROUP, STUDENT_GROUP, PARENT_GROUP]

# Maps the legacy `role` field to the Group it corresponds to.
ROLE_TO_GROUP = {
    'ADMIN': ADMIN_GROUP,
    'TEACHER': TEACHER_GROUP,
    'STUDENT': STUDENT_GROUP,
    'PARENT': PARENT_GROUP,
}


# Custom permission codenames (accounts.Profile Meta.permissions), assigned to
# Groups in the admin panel — these, not raw group membership, gate the group
# dashboards and privileged school-operations tooling.
TEACHER_DASHBOARD_PERM = 'accounts.access_teacher_dashboard'
STUDENT_DASHBOARD_PERM = 'accounts.access_student_dashboard'
PARENT_DASHBOARD_PERM = 'accounts.access_parent_dashboard'
MANAGE_SCHOOL_OPERATIONS_PERM = 'accounts.manage_school_operations'


def user_in_group(user, *group_names):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=group_names).exists()


def can_manage_school_operations(user):
    """Staff or holders of the manage_school_operations permission (assigned via Group or user in admin)."""
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.is_staff or user.has_perm(MANAGE_SCHOOL_OPERATIONS_PERM)


def primary_group_name(user):
    """Return the group that should drive redirects/UI for this user, falling back to `role`."""
    if not getattr(user, 'is_authenticated', False):
        return None
    group = user.groups.filter(name__in=ALL_GROUPS).values_list('name', flat=True).first()
    if group:
        return group
    return ROLE_TO_GROUP.get(str(getattr(user, 'role', '')).upper())


def group_required(*group_names):
    """View decorator restricting access to members of any of the given groups (staff/superusers always pass)."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/accounts/login/?next={request.path}")
            if request.user.is_staff or request.user.is_superuser or user_in_group(request.user, *group_names):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access that page.")
            raise PermissionDenied("You don't have permission to access that page.")
        return _wrapped
    return decorator


def permission_required_view(*perm_codenames):
    """View decorator restricting access to users holding any of the given Django permissions
    (via their Group or granted directly to the user in the admin panel). Staff/superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/accounts/login/?next={request.path}")
            if request.user.is_staff or any(request.user.has_perm(perm) for perm in perm_codenames):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access that page.")
            raise PermissionDenied("You don't have permission to access that page.")
        return _wrapped
    return decorator
