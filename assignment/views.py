# Create your views here.

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from accounts.permissions import group_required, TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP
from .models import Assignment, Submission

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def assignment_list(request):
    assignments = Assignment.objects.all().order_by('-due_date')
    return render(request, 'assignments/list.html', {'assignments': assignments})

@group_required(TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP)
def submit_assignment_ajax(request, pk):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, pk=pk)
        text = request.POST.get('submission_text', '')
        file = request.FILES.get('file_upload')

        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            submission_text=text,
            file_upload=file
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Assignment submitted successfully!',
            'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)