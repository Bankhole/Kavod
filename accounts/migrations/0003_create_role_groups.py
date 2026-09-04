from django.db import migrations


GROUP_NAMES = ['Admin', 'Teacher', 'Student', 'Alumni']

ROLE_TO_GROUP = {
    'ADMIN': 'Admin',
    'TEACHER': 'Teacher',
    'STUDENT': 'Student',
    'ALUMNI': 'Alumni',
}


def create_groups_and_backfill(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('accounts', 'User')

    groups = {}
    for name in GROUP_NAMES:
        group, _ = Group.objects.get_or_create(name=name)
        groups[name] = group

    for user in User.objects.all():
        group_name = ROLE_TO_GROUP.get(str(user.role).upper())
        if group_name:
            user.groups.add(groups[group_name])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_address_profile_city_profile_country_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_backfill, noop_reverse),
    ]
