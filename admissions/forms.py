# forms.py
from django import forms
from .models import AdmissionApplication

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = ['full_name', 'date_of_birth', 'parent_name', 'email', 'phone', 'target_class', 'previous_school']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Student's Full Name"}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent/Guardian Name"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+234...'}),
            'target_class': forms.Select(attrs={'class': 'form-select'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last school attended'}),
        }