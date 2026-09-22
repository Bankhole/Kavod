# Create your views here.
# attendance/views.py
import json
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.permissions import (
    group_required, user_in_group,
    TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP, PARENT_GROUP,
)
from .models import AcademicSession, Subject, StudentClass, Student, AttendanceHeader, AttendanceRecord

def attendance_dashboard(request):
    if not request.user.is_authenticated:
        return redirect(f'/accounts/login/?next={request.path}')
    if request.user.is_staff or user_in_group(request.user, TEACHER_GROUP, ADMIN_GROUP):
        return _teacher_attendance_dashboard(request)
    if user_in_group(request.user, STUDENT_GROUP):
        return student_attendance(request)
    raise PermissionDenied("You don't have permission to access attendance.")


def _teacher_attendance_dashboard(request):
    sessions = AcademicSession.objects.all()
    subjects = Subject.objects.all()
    classes = StudentClass.objects.all()
    return render(request, 'attendance/dashboard.html', {
        'sessions': sessions,
        'subjects': subjects,
        'classes': classes,
    })


@login_required
def student_attendance(request):
    """Show a student their own read-only attendance history."""
    if not user_in_group(request.user, STUDENT_GROUP):
        raise PermissionDenied("You don't have permission to access student attendance.")

    student = Student.objects.filter(
        first_name=request.user.first_name,
        last_name=request.user.last_name,
    ).select_related('student_class').first()
    records = AttendanceRecord.objects.none()
    attendance_percent = 0

    if student:
        records = AttendanceRecord.objects.filter(student=student).select_related(
            'header__subject', 'header__session', 'header__student_class'
        ).order_by('-header__date')
        total_days = records.count()
        present_days = records.filter(status__in=['P', 'L']).count()
        attendance_percent = round((present_days / total_days) * 100) if total_days else 0

    return render(request, 'attendance/student_attendance.html', {
        'student': student,
        'records': records,
        'attendance_percent': attendance_percent,
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


@group_required(PARENT_GROUP)
def parent_attendance(request):
    """Read-only attendance summary for the children linked to the logged-in parent."""
    children = Student.objects.filter(parent=request.user).select_related('student_class')

    child_reports = []
    for child in children:
        records = AttendanceRecord.objects.filter(student=child).select_related('header', 'header__subject', 'header__session')
        total_days = records.count()
        present_days = records.filter(status__in=['P', 'L']).count()
        attendance_percent = round((present_days / total_days) * 100) if total_days else 0
        child_reports.append({
            'child': child,
            'records': records.order_by('-header__date'),
            'total_days': total_days,
            'present_days': present_days,
            'attendance_percent': attendance_percent,
        })

    return render(request, 'attendance/parent_attendance.html', {'child_reports': child_reports})