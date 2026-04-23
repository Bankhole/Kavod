"""
Auto migration to reconcile DB schema with current models:
- Rename table `exams_choice` -> `exams_option` if needed
- Rename column `question_text` -> `text` on `exams_question` if needed

This migration uses a RunPython operation that checks the sqlite_master
and performs safe ALTERs; it also includes a fallback for renaming a column
by creating a new table and copying data when the SQLite version doesn't
support `ALTER TABLE ... RENAME COLUMN`.
"""
from django.db import migrations, connection


def forwards(apps, schema_editor):
    # Use direct DB cursor because we're manipulating raw tables
    conn = connection
    cursor = conn.cursor()

    # 1) Rename table exams_choice -> exams_option if necessary
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_choice'")
    has_choice = cursor.fetchone() is not None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_option'")
    has_option = cursor.fetchone() is not None

    if has_choice and not has_option:
        cursor.execute('ALTER TABLE exams_choice RENAME TO exams_option')

    # 2) Rename column question_text -> text on exams_question if necessary
    cursor.execute("PRAGMA table_info('exams_question')")
    cols = [r[1] for r in cursor.fetchall()]
    has_qtext = 'question_text' in cols
    has_text = 'text' in cols

    if has_qtext and not has_text:
        # Try simple rename first (works on SQLite >= 3.25.0)
        try:
            cursor.execute('ALTER TABLE exams_question RENAME COLUMN question_text TO text')
        except Exception:
            # Fallback: create a new table with the desired schema and copy data
            # Build the new table - reflect the model fields
            # Note: adjust column types if your model expects different types
            cursor.execute('PRAGMA foreign_keys=off')
            cursor.execute('CREATE TABLE exams_question_new (id INTEGER PRIMARY KEY, text varchar(255), marks INTEGER, quiz_id INTEGER)')
            cursor.execute('INSERT INTO exams_question_new (id, text, marks, quiz_id) SELECT id, question_text, marks, quiz_id FROM exams_question')
            cursor.execute('DROP TABLE exams_question')
            cursor.execute('ALTER TABLE exams_question_new RENAME TO exams_question')
            cursor.execute('PRAGMA foreign_keys=on')


def backwards(apps, schema_editor):
    conn = connection
    cursor = conn.cursor()

    # Reverse: rename exams_option -> exams_choice if exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_option'")
    has_option = cursor.fetchone() is not None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_choice'")
    has_choice = cursor.fetchone() is not None
    if has_option and not has_choice:
        cursor.execute('ALTER TABLE exams_option RENAME TO exams_choice')

    # Reverse column rename text -> question_text
    cursor.execute("PRAGMA table_info('exams_question')")
    cols = [r[1] for r in cursor.fetchall()]
    has_text = 'text' in cols
    has_qtext = 'question_text' in cols
    if has_text and not has_qtext:
        try:
            cursor.execute('ALTER TABLE exams_question RENAME COLUMN text TO question_text')
        except Exception:
            # Fallback: recreate old table shape
            cursor.execute('PRAGMA foreign_keys=off')
            cursor.execute('CREATE TABLE exams_question_old (id INTEGER PRIMARY KEY, question_text varchar(255), marks INTEGER, quiz_id INTEGER)')
            cursor.execute('INSERT INTO exams_question_old (id, question_text, marks, quiz_id) SELECT id, text, marks, quiz_id FROM exams_question')
            cursor.execute('DROP TABLE exams_question')
            cursor.execute('ALTER TABLE exams_question_old RENAME TO exams_question')
            cursor.execute('PRAGMA foreign_keys=on')


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
