from django.shortcuts import render, get_object_or_404
from .models import Announcement


def announcement_list(request):
    queryset = Announcement.objects.filter(is_published=True)
    audience = request.GET.get('audience')
    if audience in ['STUDENTS', 'TEACHERS', 'PARENTS']:
        queryset = queryset.filter(target_audience__in=[audience, 'ALL'])

    context = {
        'announcements': queryset,
        'current_filter': audience or 'ALL',
    }
    return render(request, 'announcements/list.html', context)


def announcement_detail(request, slug):
    announcement = get_object_or_404(Announcement, slug=slug, is_published=True)
    return render(request, 'announcements/detail.html', {'announcement': announcement})
