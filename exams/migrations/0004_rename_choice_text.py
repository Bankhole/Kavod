"""
Rename column `choice_text` to `text` on `exams_option`.

This migration attempts to use ALTER TABLE ... RENAME COLUMN and falls back
to the create-copy-drop pattern for older SQLite versions. It is reversible.
"""
from django.db import migrations, connection


def forwards(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info('exams_option')")
    cols = [r[1] for r in cursor.fetchall()]
    has_choice_text = 'choice_text' in cols
    has_text = 'text' in cols

    if has_choice_text and not has_text:
        # Try ALTER TABLE RENAME COLUMN (SQLite >= 3.25)
        try:
            cursor.execute("ALTER TABLE exams_option RENAME COLUMN choice_text TO text")
            return
        except Exception:
            pass

        # Fallback: create new table with desired schema and copy data
        cursor.execute('PRAGMA foreign_keys=off')
        cursor.execute('''
            CREATE TABLE exams_option_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text varchar(255) NOT NULL,
                is_correct bool NOT NULL DEFAULT 0,
                question_id bigint NOT NULL
            );
        ''')
        # Copy data from old to new (map choice_text -> text)
        cursor.execute('INSERT INTO exams_option_new (id, text, is_correct, question_id) SELECT id, choice_text, is_correct, question_id FROM exams_option')
        cursor.execute('DROP TABLE exams_option')
        cursor.execute('ALTER TABLE exams_option_new RENAME TO exams_option')
        cursor.execute('PRAGMA foreign_keys=on')


def backwards(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info('exams_option')")
    cols = [r[1] for r in cursor.fetchall()]
    has_text = 'text' in cols
    has_choice_text = 'choice_text' in cols

    if has_text and not has_choice_text:
        try:
            cursor.execute("ALTER TABLE exams_option RENAME COLUMN text TO choice_text")
            return
        except Exception:
            pass

        cursor.execute('PRAGMA foreign_keys=off')
        cursor.execute('''
            CREATE TABLE exams_option_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                choice_text varchar(200) NOT NULL,
                is_correct bool NOT NULL DEFAULT 0,
                question_id bigint NOT NULL
            );
        ''')
        cursor.execute('INSERT INTO exams_option_old (id, choice_text, is_correct, question_id) SELECT id, text, is_correct, question_id FROM exams_option')
        cursor.execute('DROP TABLE exams_option')
        cursor.execute('ALTER TABLE exams_option_old RENAME TO exams_option')
        cursor.execute('PRAGMA foreign_keys=on')


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0003_create_results_useranswers'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
