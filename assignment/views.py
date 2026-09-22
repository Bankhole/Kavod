# Create your views here.

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from accounts.permissions import group_required, TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP
from .models import Assignment, Submission

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def assignment_list(request):
    if request.user.role == 'STUDENT':
        assignments = Assignment.objects.filter(
            Q(student_class__isnull=True) | Q(student_class=request.user.profile.student_class)
        ).order_by('-due_date')
    else:
        assignments = Assignment.objects.all().order_by('-due_date')
    return render(request, 'assignments/list.html', {'assignments': assignments})

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def submit_assignment_ajax(request, pk):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, pk=pk)
        if request.user.role == 'STUDENT' and assignment.student_class_id not in (None, request.user.profile.student_class_id):
            return JsonResponse({'status': 'error', 'message': 'This assignment is not assigned to your class.'}, status=403)

        text = request.POST.get('submission_text', '')
        file = request.FILES.get('file_upload')
        if not text.strip() and not file:
            return JsonResponse({'status': 'error', 'message': 'Add submission notes or attach a file.'}, status=400)

        submission, _ = Submission.objects.update_or_create(
            assignment=assignment,
            student=request.user,
            defaults={'submission_text': text, **({'file_upload': file} if file else {})},
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Assignment submitted successfully!',
            'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)