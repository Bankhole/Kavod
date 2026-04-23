from django.db import migrations
import math


def seconds_to_minutes(apps, schema_editor):
    Quiz = apps.get_model('exams', 'Quiz')
    for quiz in Quiz.objects.exclude(duration__isnull=True):
        # assume stored value is currently seconds; convert to minutes, rounding up
        seconds = quiz.duration
        minutes = math.ceil(seconds / 60)
        quiz.duration = minutes
        quiz.save(update_fields=['duration'])


def minutes_to_seconds(apps, schema_editor):
    Quiz = apps.get_model('exams', 'Quiz')
    for quiz in Quiz.objects.exclude(duration__isnull=True):
        minutes = quiz.duration
        seconds = minutes * 60
        quiz.duration = seconds
        quiz.save(update_fields=['duration'])


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_quiz_duration_result_timed_out'),
    ]

    operations = [
        migrations.RunPython(seconds_to_minutes, reverse_code=minutes_to_seconds),
    ]
