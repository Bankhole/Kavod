# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from accounts.permissions import group_required, TEACHER_GROUP, STUDENT_GROUP, ADMIN_GROUP
from .models import Course, Lesson, StudentEnrollment, LessonProgress


def course_list(request):
    courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')
    return render(request, 'learning/course_list.html', {'courses': courses})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = StudentEnrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'learning/course_detail.html', context)


@group_required(STUDENT_GROUP, TEACHER_GROUP, ADMIN_GROUP)
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    
    # Verify access permission
    is_enrolled = StudentEnrollment.objects.filter(user=request.user, course=course).exists()
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    if not is_enrolled and not lesson.is_preview:
        return redirect('course_detail', slug=course.slug)

    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
    }
    return render(request, 'learning/lesson_detail.html', context)


@group_required(STUDENT_GROUP, TEACHER_GROUP, ADMIN_GROUP)
def update_lesson_progress(request, lesson_id):
    """API endpoint to record playback position asynchronously."""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        watched_seconds = int(request.POST.get('seconds', 0))
        completed = request.POST.get('completed') == 'true'

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user, 
            lesson=lesson
        )
        progress.last_watched_seconds = watched_seconds
        if completed:
            progress.completed = True
        progress.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid method'}, status=400)