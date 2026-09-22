# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Profile


class AccessCodeLoginForm(forms.Form):
    access_code = forms.CharField(
        max_length=64,
        label='Access Code',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your access code',
                'autocomplete': 'off',
            }
        ),
    )

class CustomUserCreationForm(UserCreationForm):
    """Public self-registration form.

    Only non-privileged roles may be self-selected; ADMIN/TEACHER access must be
    granted by an administrator via the admin panel (Group/role assignment).
    """
    SELF_SERVICE_ROLES = (User.Roles.STUDENT, User.Roles.PARENT)

    role = forms.ChoiceField(choices=[(choice.value, choice.label) for choice in SELF_SERVICE_ROLES])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password1', None)
        self.fields.pop('password2', None)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = forms.ModelForm.save(self, commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user

    def clean_role(self):
        role = self.cleaned_data['role']
        allowed = {choice.value for choice in self.SELF_SERVICE_ROLES}
        if role not in allowed:
            role = User.Roles.STUDENT
        return role

class AdminUserCreationForm(UserCreationForm):
    """Used only by the Django admin's "Add user" form, which requires password1/password2."""

    role = forms.ChoiceField(choices=User.Roles.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs['placeholder'] = field.label

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs['placeholder'] = field.label

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'phone_number', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs['placeholder'] = field.label