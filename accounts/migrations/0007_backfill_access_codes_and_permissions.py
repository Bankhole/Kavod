import secrets

from django.db import migrations


def generate_code():
    return f"NX-{secrets.token_hex(4).upper()}"


def backfill_access_codes_and_assign_permissions(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    existing_codes = set(Profile.objects.exclude(access_code='').values_list('access_code', flat=True))
    for profile in Profile.objects.filter(access_code=''):
        code = generate_code()
        while code in existing_codes:
            code = generate_code()
        existing_codes.add(code)
        profile.access_code = code
        profile.save(update_fields=['access_code'])

    perms = Permission.objects.filter(
        content_type__app_label='accounts',
        codename__in=[
            'access_teacher_dashboard',
            'access_student_dashboard',
            'access_parent_dashboard',
            'manage_school_operations',
        ],
    )
    perm_by_codename = {perm.codename: perm for perm in perms}

    group_perm_map = {
        'Teacher': ['access_teacher_dashboard', 'manage_school_operations'],
        'Student': ['access_student_dashboard'],
        'Parent': ['access_parent_dashboard'],
    }
    for group_name, codenames in group_perm_map.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for codename in codenames:
            perm = perm_by_codename.get(codename)
            if perm:
                group.permissions.add(perm)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_profile_options_profile_access_code'),
    ]

    operations = [
        migrations.RunPython(backfill_access_codes_and_assign_permissions, noop_reverse),
    ]
