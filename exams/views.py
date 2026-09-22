from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from .models import (
    Quiz,
    Question,
    Result,
    UserAnswer,
    Option,
    StudentResultSheet,
    StudentResultSubject,
    StudentAttendanceRecord,
)
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponseForbidden
from decimal import Decimal
import json

# ----------------------------------------------------------------------
# Utility Function for Automatic Scoring
# ----------------------------------------------------------------------

@transaction.atomic
def calculate_score(user, quiz, submitted_data, timed_out=False):
    """Processes submitted answers, calculates the score, and saves the results."""
    
    # Get or create a Result object for the user/quiz combination
    # You might want to prevent re-takes, but this example allows them by updating the score
    result = Result.objects.create(user=user, quiz=quiz, score=0, timed_out=timed_out)
    
    questions = quiz.questions.all()
    
    for question in questions:
        # Get the ID of the selected option from the submitted form data
        submitted_option_id = submitted_data.get(f'question_{question.id}')
        
        selected_option = None
        is_correct = False
        
        if submitted_option_id:
            try:
                # Find the selected Option object
                selected_option = Option.objects.get(id=submitted_option_id, question=question)
            except Option.DoesNotExist:
                pass

            # Check for correctness and award marks
            if selected_option and selected_option.is_correct:
                is_correct = True
                result.score += question.marks
            
        # Save the User's specific answer
        UserAnswer.objects.create(
            result=result,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )
    
    result.save()
    return result

# ----------------------------------------------------------------------
# Views for the Quiz Application
# ----------------------------------------------------------------------

@login_required
def quiz_list(request):
    """View to display the list of all available quizzes (the exam hub page)."""
    
    available_quizzes = Quiz.objects.all()
    
    context = {
        'quizzes': available_quizzes,
        'page_title': 'Available Exams',
    }
    
    return render(request, 'exams/quiz_list.html', context)


@login_required
def take_quiz(request, quiz_id):
    """View to display a single quiz and handle its submission."""
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('options')

    session_key = f'quiz_{quiz.id}_start_time'

    # If the quiz has a duration and we don't yet have a start time, record it
    if quiz.duration and session_key not in request.session:
        # Store ISO format timestamp so it's JSON serializable in the session
        request.session[session_key] = timezone.now().isoformat()

    if request.method == 'POST':
        # Require authentication to submit answers; allow anonymous users to view the quiz.
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        # Server-side timeout check (in case client JS is bypassed)
        timed_out = False
        if quiz.duration:
            start_iso = request.session.get(session_key)
            if start_iso:
                try:
                    start_time = timezone.datetime.fromisoformat(start_iso)
                    # Make timezone-aware if needed
                    if timezone.is_naive(start_time):
                        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
                except Exception:
                    start_time = None

                if start_time:
                    elapsed = timezone.now() - start_time
                    # quiz.duration is in minutes now
                    if elapsed > timedelta(seconds=(quiz.duration * 60)):
                        timed_out = True

        # Calculate score and get the result object
        score_result = calculate_score(request.user, quiz, request.POST, timed_out=timed_out)

        # Clean up session start time for this quiz
        try:
            del request.session[session_key]
        except KeyError:
            pass

        # Redirect to the results page
        return redirect('exams:quiz_result', result_id=score_result.id)

    # Expose the session-stored start time to the template so JS can read it.
    # Use an empty string fallback if not present.
    context = {
        'quiz': quiz,
        'questions': questions,
        'quiz_start_iso': request.session.get(session_key, ''),
    }
    return render(request, 'exams/take_quiz.html', context)


@login_required
def quiz_result(request, result_id):
    """View to display the results of a submitted quiz."""
    
    # Ensure the user can only view their own result
    result = get_object_or_404(Result, id=result_id, user=request.user)
    
    context = {
        'result': result,
        # Fetch user answers to show correct/incorrect status if needed
        'user_answers': result.answers.all().select_related('question', 'selected_option')
    }
    
    return render(request, 'exams/quiz_result.html', context)


def _can_manage_manual_results(user):
    from accounts.permissions import can_manage_school_operations
    return can_manage_school_operations(user)


def _grade_for_score(score):
    if score >= 75:
        return 'A'
    if score >= 65:
        return 'B'
    if score >= 50:
        return 'C'
    if score >= 45:
        return 'D'
    if score >= 40:
        return 'E'
    return 'F'


@login_required
@user_passes_test(_can_manage_manual_results)
@transaction.atomic
def manual_result_upload(request, sheet_id=None):
    User = get_user_model()
    students = User.objects.filter(role='STUDENT').order_by('first_name', 'last_name', 'username')
    sheet = None

    if sheet_id is not None:
        sheet = get_object_or_404(
            StudentResultSheet.objects.select_related('student').prefetch_related('subjects', 'attendance_records'),
            id=sheet_id,
        )

    initial = {
        'student_id': sheet.student_id if sheet else '',
        'admission_number': sheet.admission_number if sheet else '',
        'class_name': sheet.class_name if sheet else '',
        'term': sheet.term if sheet else '',
        'session_name': sheet.session_name if sheet else '',
        'teacher_remark': sheet.teacher_remark if sheet else '',
        'principal_remark': sheet.principal_remark if sheet else '',
        'principal_sign_date': sheet.principal_sign_date.isoformat() if sheet and sheet.principal_sign_date else '',
    }

    attendance_initial = []
    subjects_initial = []
    if sheet:
        attendance_initial = [
            {
                'date': rec.date.isoformat(),
                'status': rec.status,
                'remark': rec.remark or '',
            }
            for rec in sheet.attendance_records.all()
        ]
        subjects_initial = [
            {
                'subject': row.subject,
                'ca': float(row.ca_score),
                'exam': float(row.exam_score),
            }
            for row in sheet.subjects.all()
        ]

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        admission_number = (request.POST.get('admission_number') or '').strip()
        class_name = (request.POST.get('class_name') or '').strip()
        term = (request.POST.get('term') or '').strip()
        session_name = (request.POST.get('session_name') or '').strip()
        teacher_remark = (request.POST.get('teacher_remark') or '').strip()
        principal_remark = (request.POST.get('principal_remark') or '').strip()
        principal_sign_date = request.POST.get('principal_sign_date') or None
        student_photo = request.FILES.get('student_photo')
        teacher_signature = request.FILES.get('teacher_signature')
        principal_signature = request.FILES.get('principal_signature')

        attendance_payload = request.POST.get('attendance_payload') or '[]'
        subjects_payload = request.POST.get('subjects_payload') or '[]'

        if not student_id:
            messages.error(request, 'Please select a student.')
            return render(
                request,
                'exams/manual_result_upload.html',
                {
                    'students': students,
                    'sheet': sheet,
                    'initial': initial,
                    'attendance_initial_json': json.dumps(attendance_initial),
                    'subjects_initial_json': json.dumps(subjects_initial),
                },
            )

        student = get_object_or_404(User, id=student_id)
        if sheet is None:
            sheet = StudentResultSheet.objects.create(
                student=student,
                uploaded_by=request.user,
                admission_number=admission_number,
                class_name=class_name,
                term=term,
                session_name=session_name,
                teacher_remark=teacher_remark,
                principal_remark=principal_remark,
                principal_sign_date=principal_sign_date,
                student_photo=student_photo,
                teacher_signature=teacher_signature,
                principal_signature=principal_signature,
            )
        else:
            sheet.student = student
            sheet.uploaded_by = request.user
            sheet.admission_number = admission_number
            sheet.class_name = class_name
            sheet.term = term
            sheet.session_name = session_name
            sheet.teacher_remark = teacher_remark
            sheet.principal_remark = principal_remark
            sheet.principal_sign_date = principal_sign_date
            if student_photo:
                sheet.student_photo = student_photo
            if teacher_signature:
                sheet.teacher_signature = teacher_signature
            if principal_signature:
                sheet.principal_signature = principal_signature
            sheet.save()

            # Replace row-level records with newly submitted rows on update.
            sheet.subjects.all().delete()
            sheet.attendance_records.all().delete()

        try:
            subjects_data = json.loads(subjects_payload)
        except json.JSONDecodeError:
            subjects_data = []

        total_marks = Decimal('0')
        subject_count = 0
        for item in subjects_data:
            subject_name = (item.get('subject') or '').strip()
            if not subject_name:
                continue

            ca = Decimal(str(item.get('ca', 0) or 0))
            exam = Decimal(str(item.get('exam', 0) or 0))
            total = ca + exam
            grade = _grade_for_score(float(total))

            StudentResultSubject.objects.create(
                result_sheet=sheet,
                subject=subject_name,
                ca_score=ca,
                exam_score=exam,
                total_score=total,
                grade=grade,
            )
            total_marks += total
            subject_count += 1

        try:
            attendance_data = json.loads(attendance_payload)
        except json.JSONDecodeError:
            attendance_data = []

        for item in attendance_data:
            rec_date = item.get('date')
            status = item.get('status')
            remark = (item.get('remark') or '').strip()
            if rec_date and status:
                StudentAttendanceRecord.objects.create(
                    result_sheet=sheet,
                    date=rec_date,
                    status=status,
                    remark=remark,
                )

        average = total_marks / subject_count if subject_count else Decimal('0')
        sheet.total_marks = total_marks
        sheet.average_score = average
        sheet.overall_grade = _grade_for_score(float(average)) if subject_count else ''
        sheet.save(update_fields=['total_marks', 'average_score', 'overall_grade'])

        if sheet_id is None:
            messages.success(request, 'Result sheet saved successfully.')
        else:
            messages.success(request, 'Result sheet updated successfully.')
        return redirect('exams:result_sheet_detail', sheet_id=sheet.id)

    return render(
        request,
        'exams/manual_result_upload.html',
        {
            'students': students,
            'sheet': sheet,
            'initial': initial,
            'attendance_initial_json': json.dumps(attendance_initial),
            'subjects_initial_json': json.dumps(subjects_initial),
        },
    )


@login_required
def check_results(request):
    # Parents see their own children's sheets too, grouped by student for clarity.
    child_ids = list(request.user.children_profiles.values_list('user_id', flat=True))
    student_ids = [request.user.id] + child_ids
    sheets = StudentResultSheet.objects.filter(student_id__in=student_ids).select_related('student').prefetch_related('subjects', 'attendance_records')
    return render(request, 'exams/check_results.html', {'sheets': sheets, 'has_children': bool(child_ids)})


@login_required
def result_sheet_detail(request, sheet_id):
    sheet = get_object_or_404(
        StudentResultSheet.objects.select_related('student', 'uploaded_by').prefetch_related('subjects', 'attendance_records'),
        id=sheet_id,
    )

    is_own_sheet = sheet.student_id == request.user.id
    is_own_childs_sheet = request.user.children_profiles.filter(user_id=sheet.student_id).exists()
    if not is_own_sheet and not is_own_childs_sheet and not _can_manage_manual_results(request.user):
        return HttpResponseForbidden('You are not allowed to view this result sheet.')

    total_days = sheet.attendance_records.count()
    present_days = sheet.attendance_records.filter(status__in=['Present', 'Late']).count()
    attendance_percent = round((present_days / total_days) * 100) if total_days else 0

    context = {
        'sheet': sheet,
        'total_days': total_days,
        'present_days': present_days,
        'attendance_percent': attendance_percent,
        'can_manage_manual_results': _can_manage_manual_results(request.user),
    }
    return render(request, 'exams/result_sheet_detail.html', context)
