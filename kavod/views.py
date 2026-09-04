from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from announcements.models import Announcement


def home(request):
    announcements = Announcement.objects.filter(is_published=True).order_by('-is_important', '-created_at')[:5]
    return render(request, 'home.html', {'announcements': announcements})


@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def admissions(request):
    return render(request, 'admissions.html')


@login_required
def academics(request):
    return render(request, 'academics.html')


@login_required
def contact(request):
    return render(request, 'contact.html')
