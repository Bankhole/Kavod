from django.db import migrations, connection


def forwards(apps, schema_editor):
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exams_result'")
    if cursor.fetchone() is None:
        return

    cursor.execute("PRAGMA foreign_key_list('exams_result')")
    fk_rows = cursor.fetchall()
    fk_targets = [row[2] for row in fk_rows if row[3] == 'user_id']

    # Already pointing at custom user table; nothing to do.
    if 'accounts_user' in fk_targets:
        return

    cursor.execute("PRAGMA table_info('exams_result')")
    cols = [row[1] for row in cursor.fetchall()]
    has_timed_out = 'timed_out' in cols

    cursor.execute('PRAGMA foreign_keys=off')

    cursor.execute(
        '''
        CREATE TABLE exams_result_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL DEFAULT 0,
            date_taken DATETIME NOT NULL,
            timed_out BOOLEAN NOT NULL DEFAULT 0,
            quiz_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES exams_quiz(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES accounts_user(id) ON DELETE CASCADE
        )
        '''
    )

    timed_out_expr = 'timed_out' if has_timed_out else '0'
    # If a legacy user_id does not exist in accounts_user, attach result to the first account user.
    # This avoids migration failure while preserving result rows.
    cursor.execute(
        f'''
        INSERT INTO exams_result_new (id, score, date_taken, timed_out, quiz_id, user_id)
        SELECT
            r.id,
            r.score,
            r.date_taken,
            {timed_out_expr},
            r.quiz_id,
            CASE
                WHEN EXISTS(SELECT 1 FROM accounts_user u WHERE u.id = r.user_id) THEN r.user_id
                ELSE (SELECT id FROM accounts_user ORDER BY id LIMIT 1)
            END
        FROM exams_result r
        '''
    )

    cursor.execute('DROP TABLE exams_result')
    cursor.execute('ALTER TABLE exams_result_new RENAME TO exams_result')
    cursor.execute('PRAGMA foreign_keys=on')


def backwards(apps, schema_editor):
    # No reverse operation needed for this corrective migration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0009_studentresultsheet_principal_signature_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
