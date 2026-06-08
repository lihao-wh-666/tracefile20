from django.db import migrations


def setup_archive_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    entry_group, created = Group.objects.get_or_create(name='案卷管理录入组')
    review_group, created = Group.objects.get_or_create(name='案卷管理审核组')

    try:
        content_type = ContentType.objects.get(app_label='archives', model='archive')
    except ContentType.DoesNotExist:
        return

    permissions = Permission.objects.filter(content_type=content_type)

    add_permission = permissions.filter(codename='add_archive').first()
    change_permission = permissions.filter(codename='change_archive').first()
    view_permission = permissions.filter(codename='view_archive').first()

    if add_permission:
        entry_group.permissions.add(add_permission)
    if change_permission:
        entry_group.permissions.add(change_permission)
        review_group.permissions.add(change_permission)
    if view_permission:
        entry_group.permissions.add(view_permission)
        review_group.permissions.add(view_permission)


def remove_archive_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['案卷管理录入组', '案卷管理审核组']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0004_archive_review_and_todo_enhancement'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(setup_archive_groups, remove_archive_groups),
    ]
