from django.db import migrations


def rename_alumni_to_parent(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('accounts', 'User')

    Group.objects.filter(name='Alumni').update(name='Parent')
    User.objects.filter(role='ALUMNI').update(role='PARENT')


def rename_parent_to_alumni(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('accounts', 'User')

    Group.objects.filter(name='Parent').update(name='Alumni')
    User.objects.filter(role='PARENT').update(role='ALUMNI')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(rename_alumni_to_parent, rename_parent_to_alumni),
    ]
