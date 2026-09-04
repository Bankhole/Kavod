# Create your views here.
# attendance/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.permissions import group_required, TEACHER_GROUP, ADMIN_GROUP
from .models import AcademicSession, Subject, StudentClass, Student, AttendanceHeader, AttendanceRecord

@group_required(TEACHER_GROUP, ADMIN_GROUP)
def attendance_dashboard(request):
    sessions = AcademicSession.objects.all()
    subjects = Subject.objects.all()
    classes = StudentClass.objects.all()
    return render(request, 'attendance/dashboard.html', {
        'sessions': sessions,
        'subjects': subjects,
        'classes': classes,
    })

@group_required(TEACHER_GROUP, ADMIN_GROUP)
def get_students(request):
    class_id = request.GET.get('class_id')
    students = Student.objects.filter(student_class_id=class_id).values('id', 'roll_number', 'first_name', 'last_name')
    return JsonResponse({'students': list(students)})

@group_required(TEACHER_GROUP, ADMIN_GROUP)
def save_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            subject_id = data.get('subject_id')
            class_id = data.get('class_id')
            date = data.get('date')
            attendance_data = data.get('attendance', {})

            # Create or update Attendance Header
            header, created = AttendanceHeader.objects.get_or_create(
                session_id=session_id,
                subject_id=subject_id,
                student_class_id=class_id,
                date=date,
                defaults={'teacher': request.user}
            )

            # Update Records
            for student_id, status in attendance_data.items():
                AttendanceRecord.objects.update_or_create(
                    header=header,
                    student_id=student_id,
                    defaults={'status': status}
                )

            return JsonResponse({'status': 'success', 'message': 'Attendance saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)