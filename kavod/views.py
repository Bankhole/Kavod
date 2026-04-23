
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def admissions(request):
    return render(request, 'admissions.html')

def academics(request):
    return render(request, 'academics.html')

def contact(request):
    return render(request, 'contact.html')
