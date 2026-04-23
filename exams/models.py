from django.db import models
from django.contrib.auth.models import User

# Model for the main Exam/Quiz
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    # Duration of the quiz in minutes. If null, there is no time limit.
    duration = models.IntegerField(null=True, blank=True, help_text='Duration in minutes. Null for no limit.')
    
    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

# Model for individual Questions
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    marks = models.IntegerField(default=1) # Marks awarded for a correct answer

    def __str__(self):
        return self.text[:50] + '...'

# Model for the Multiple Choice Options
class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False) # The key to scoring!

    def __str__(self):
        return self.text

# Model to store the User's overall Result
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    # Whether the result was produced because the quiz timed out
    timed_out = models.BooleanField(default=False)
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s result for {self.quiz.title}"

# Model to store a User's specific answer for a question
class UserAnswer(models.Model):
    result = models.ForeignKey(Result, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False) # Set by the scoring logic

    class Meta:
        # Ensures a user only has one answer per question per result
        unique_together = ('result', 'question') 
        
    def __str__(self):
        return f"Q: {self.question.id} - Correct: {self.is_correct}"