# accounts/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, View, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .forms import AccessCodeLoginForm, CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from .permissions import (
    primary_group_name, permission_required_view,
    TEACHER_DASHBOARD_PERM, STUDENT_DASHBOARD_PERM, PARENT_DASHBOARD_PERM,
)


# Landing page for each Group once a user logs in, so people only see the
# functionality approved for their assigned group.
GROUP_LANDING_URLS = {
    'Admin': 'admin:index',
    'Teacher': 'accounts:teacher_dashboard',
    'Student': 'accounts:student_dashboard',
    'Parent': 'accounts:parent_dashboard',
}


@login_required
def dashboard_redirect(request):
    """Send a freshly logged-in user to the section approved for their Group."""
    if request.user.is_staff or request.user.is_superuser:
        return redirect(reverse('admin:index'))
    group_name = primary_group_name(request.user)
    url_name = GROUP_LANDING_URLS.get(group_name, 'home')
    return redirect(reverse(url_name))


@permission_required_view(TEACHER_DASHBOARD_PERM)
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')


@permission_required_view(STUDENT_DASHBOARD_PERM)
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')


@permission_required_view(PARENT_DASHBOARD_PERM)
def parent_dashboard(request):
    return render(request, 'accounts/parent_dashboard.html')


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        access_code = self.object.profile.access_code
        messages.success(
            self.request,
            f"Account created successfully! Your unique access code is {access_code}. "
            "An administrator must issue this code to you before you can log in with it.",
        )
        return response


class UserLoginView(View):
    template_name = 'accounts/login.html'

    ACCESS_CODE_CONFIG = {
        'ADMIN': {
            'setting': 'KAVOD_ADMIN_ACCESS_CODE',
            'default': 'KAVOD-ADMIN-2026',
            'username': 'portal_admin',
            'email': 'portal_admin@kavod.local',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        },
        'STAFF': {
            'setting': 'KAVOD_STAFF_ACCESS_CODE',
            'default': 'KAVOD-STAFF-2026',
            'username': 'portal_staff',
            'email': 'portal_staff@kavod.local',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': False,
        },
        'TEACHER': {
            'setting': 'KAVOD_TEACHER_ACCESS_CODE',
            'default': 'KAVOD-TEACHER-2026',
            'username': 'portal_teacher',
            'email': 'portal_teacher@kavod.local',
            'role': 'TEACHER',
            'is_staff': False,
            'is_superuser': False,
        },
        'PARENT': {
            'setting': 'KAVOD_PARENT_ACCESS_CODE',
            'default': 'KAVOD-PARENT-2026',
            'username': 'portal_parent',
            'email': 'portal_parent@kavod.local',
            'role': 'PARENT',
            'is_staff': False,
            'is_superuser': False,
        },
    }

    def _resolved_codes(self):
        resolved = {}
        for key, cfg in self.ACCESS_CODE_CONFIG.items():
            resolved[key] = getattr(settings, cfg['setting'], cfg['default'])
        return resolved

    def _get_or_create_access_user(self, role_key):
        cfg = self.ACCESS_CODE_CONFIG[role_key]
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=cfg['username'],
            defaults={
                'email': cfg['email'],
                'role': cfg['role'],
                'is_staff': cfg['is_staff'],
                'is_superuser': cfg['is_superuser'],
                'is_active': True,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])

        updates = []
        if user.email != cfg['email']:
            user.email = cfg['email']
            updates.append('email')
        if user.role != cfg['role']:
            user.role = cfg['role']
            updates.append('role')
        if user.is_staff != cfg['is_staff']:
            user.is_staff = cfg['is_staff']
            updates.append('is_staff')
        if user.is_superuser != cfg['is_superuser']:
            user.is_superuser = cfg['is_superuser']
            updates.append('is_superuser')
        if not user.is_active:
            user.is_active = True
            updates.append('is_active')

        if updates:
            user.save(update_fields=updates)

        return user

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return render(request, self.template_name, {'form': AccessCodeLoginForm()})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())

        form = AccessCodeLoginForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        submitted_code = form.cleaned_data['access_code'].strip()

        # Individually registered users log in with their own unique code first.
        profile = Profile.objects.select_related('user').filter(access_code=submitted_code).first()
        if profile:
            if not profile.user.is_active:
                messages.error(request, 'This account has been deactivated. Contact the school administrator.')
                return render(request, self.template_name, {'form': form})
            login(request, profile.user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {profile.user.get_full_name() or profile.user.username}!')
            return redirect(self.get_success_url())

        code_map = self._resolved_codes()

        matching_role = None
        for role_key, code_value in code_map.items():
            if submitted_code == str(code_value):
                matching_role = role_key
                break

        if not matching_role:
            messages.error(request, 'Invalid access code. Please try again.')
            return render(request, self.template_name, {'form': form})

        user = self._get_or_create_access_user(matching_role)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'Signed in with {matching_role.title()} access.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return reverse_lazy('accounts:dashboard_redirect')


class UserLogoutView(LoginRequiredMixin, View):
    template_name = 'accounts/logout_confirm.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('accounts:logout_success')


class LogoutSuccessView(TemplateView):
    template_name = 'accounts/logout_success.html'


class EditProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        return render(request, self.template_name, {'u_form': u_form, 'p_form': p_form, 'profile': profile})

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your portal profile has been updated!")
            return redirect('accounts:profile')

        return render(request, self.template_name, {'u_form': u_form, 'p_form': p_form, 'profile': profile})


