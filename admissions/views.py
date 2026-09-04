# Create your views here.

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdmissionForm

def admission_view(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been submitted successfully! We will contact you soon.')
            return redirect('admissions:admission_apply')
    else:
        form = AdmissionForm()
    
    return render(request, 'admission.html', {'form': form})
