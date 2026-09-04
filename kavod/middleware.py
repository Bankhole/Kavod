from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


class LoginRequiredMiddleware:
    """Protect private routes while allowing only authentication/system endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info
        if request.user.is_authenticated:
            return None

        if path in {'/', '/accounts/login/', '/accounts/register/'}:
            return None
        if path.startswith(settings.LOGIN_URL) or path.startswith('/accounts/register/'):
            return None
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/'):
            return None

        return redirect(f"{settings.LOGIN_URL}?next={request.path}")


class SafeDatabaseWriteMiddleware:
    """Prevent uncaught DB integrity exceptions from breaking form-save flows."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except IntegrityError:
            if request.method == 'POST':
                messages.error(
                    request,
                    'Save failed due to related data constraints. Please review the selected related records and try again.',
                )
                back_url = request.META.get('HTTP_REFERER') or request.path
                return HttpResponseRedirect(back_url)
            raise
