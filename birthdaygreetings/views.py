from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import BirthdayProfile


@login_required
def today_birthdays_view(request):
    today = timezone.now().date()
    celebrants = BirthdayProfile.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day
    ).select_related('user')

    context = {
        'celebrants': celebrants,
        'today': today,
    }
    return render(request, 'birthdaygreetings/today_birthdays.html', context)
