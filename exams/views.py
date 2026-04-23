from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Question, Result, UserAnswer, Option
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

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

def quiz_list(request):
    """View to display the list of all available quizzes (the exam hub page)."""
    
    available_quizzes = Quiz.objects.all()
    
    context = {
        'quizzes': available_quizzes,
        'page_title': 'Available Exams',
    }
    
    return render(request, 'exams/quiz_list.html', context)


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
        return redirect('quiz_result', result_id=score_result.id)

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