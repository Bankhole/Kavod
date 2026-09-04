# Create your views here.

from django.shortcuts import render, get_object_or_404
from accounts.permissions import group_required, TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP
from .models import Schedule, Classroom, TimeSlot

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def classroom_list(request):
    classrooms = Classroom.objects.all().order_by('name')
    return render(request, 'timetable/classroom_list.html', {'classrooms': classrooms})

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def timetable_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)
    time_slots = TimeSlot.objects.all()
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']

    # Fetch all scheduled periods for this specific classroom
    schedules = Schedule.objects.filter(classroom=classroom).select_related('subject', 'teacher', 'time_slot')

    # Structure data: grid[time_slot][day] = schedule_object
    grid = {slot: {day: None for day in days} for slot in time_slots}

    for schedule in schedules:
        grid[schedule.time_slot][schedule.time_slot.day] = schedule

    context = {
        'classroom': classroom,
        'days': [('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday')],
        'time_slots': time_slots,
        'grid': grid,
    }
    return render(request, 'timetable/grid.html', context)
