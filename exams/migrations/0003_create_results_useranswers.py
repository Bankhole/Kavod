"""
Create missing Result and UserAnswer tables if they don't exist.

This migration is defensive: it will only create the tables when they are absent
to reconcile the DB with migration state. It is reversible (drops the tables).
"""
from django.db import migrations, connection


def forwards(apps, schema_editor):
    cursor = connection.cursor()

    # Create exams_result if missing
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_result'")
    if cursor.fetchone() is None:
        cursor.execute('''
        CREATE TABLE exams_result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL DEFAULT 0,
            date_taken DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            quiz_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES exams_quiz(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
        );
        ''')

    # Create exams_useranswer if missing
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_useranswer'")
    if cursor.fetchone() is None:
        cursor.execute('''
        CREATE TABLE exams_useranswer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_correct BOOLEAN NOT NULL DEFAULT 0,
            question_id INTEGER NOT NULL,
            result_id INTEGER NOT NULL,
            selected_option_id INTEGER,
            FOREIGN KEY(result_id) REFERENCES exams_result(id) ON DELETE CASCADE,
            FOREIGN KEY(question_id) REFERENCES exams_question(id) ON DELETE CASCADE,
            FOREIGN KEY(selected_option_id) REFERENCES exams_option(id) ON DELETE CASCADE
        );
        ''')
        # unique constraint for (result, question)
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS exams_useranswer_result_question_uniq ON exams_useranswer(result_id, question_id);')


def backwards(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_useranswer'")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE exams_useranswer')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_result'")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE exams_result')


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_fix_schema'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
