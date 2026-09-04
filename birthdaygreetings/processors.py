from django.utils import timezone
from .models import BirthdayProfile


def todays_celebrants(request):
    today = timezone.now().date()
    celebrants = BirthdayProfile.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    ).select_related('user')

    return {
        'todays_celebrants': celebrants,
    }
