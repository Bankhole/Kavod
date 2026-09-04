from .permissions import can_manage_school_operations, primary_group_name


def permissions(request):
    """Expose Group-based permission flags to all templates (used by navbar/menus)."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {'can_manage_school_operations': False, 'user_group': None}
    return {
        'can_manage_school_operations': can_manage_school_operations(user),
        'user_group': primary_group_name(user),
    }
