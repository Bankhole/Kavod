from django.conf import settings
from django.db import models

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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


class StudentResultSheet(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='result_sheets')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_result_sheets')
    admission_number = models.CharField(max_length=50)
    class_name = models.CharField(max_length=100)
    term = models.CharField(max_length=100)
    session_name = models.CharField(max_length=100)
    student_photo = models.ImageField(upload_to='result_photos/', blank=True, null=True)
    teacher_signature = models.ImageField(upload_to='teacher_signatures/', blank=True, null=True)
    principal_signature = models.ImageField(upload_to='principal_signatures/', blank=True, null=True)
    teacher_remark = models.TextField(blank=True)
    principal_remark = models.TextField(blank=True)
    principal_sign_date = models.DateField(null=True, blank=True)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    average_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Result Sheet: {self.student.username} ({self.term})"


class StudentResultSubject(models.Model):
    result_sheet = models.ForeignKey(StudentResultSheet, on_delete=models.CASCADE, related_name='subjects')
    subject = models.CharField(max_length=120)
    ca_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.subject}: {self.total_score}"


class StudentAttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    )

    result_sheet = models.ForeignKey(StudentResultSheet, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remark = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.status}"