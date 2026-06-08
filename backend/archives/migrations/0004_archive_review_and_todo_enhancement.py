from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_created_by_to_foreign_key(apps, schema_editor):
    Archive = apps.get_model('archives', 'Archive')
    User = apps.get_model('auth', 'User')

    for archive in Archive.objects.all():
        if archive.created_by:
            try:
                user = User.objects.get(username=archive.created_by)
                archive.created_by_user = user
                archive.save()
            except User.DoesNotExist:
                pass


def reverse_migrate_created_by(apps, schema_editor):
    Archive = apps.get_model('archives', 'Archive')

    for archive in Archive.objects.all():
        if archive.created_by_user:
            archive.created_by = archive.created_by_user.username
            archive.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('archives', '0003_alter_userpreference_language_archivelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='review_comment',
            field=models.TextField(blank=True, verbose_name='审核意见'),
        ),
        migrations.AddField(
            model_name='archive',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='审核时间'),
        ),
        migrations.AddField(
            model_name='archive',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_archives', to=settings.AUTH_USER_MODEL, verbose_name='审核人'),
        ),
        migrations.AddField(
            model_name='archive',
            name='submitted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='提交审核时间'),
        ),
        migrations.AddField(
            model_name='archive',
            name='created_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_archives', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.RunPython(migrate_created_by_to_foreign_key, reverse_migrate_created_by),
        migrations.RemoveField(
            model_name='archive',
            name='created_by',
        ),
        migrations.RenameField(
            model_name='archive',
            old_name='created_by_user',
            new_name='created_by',
        ),
        migrations.AddField(
            model_name='todo',
            name='archive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='archives.archive', verbose_name='关联案卷'),
        ),
        migrations.AddField(
            model_name='todo',
            name='todo_type',
            field=models.CharField(choices=[('general', '普通'), ('review', '审核'), ('notification', '通知')], default='general', max_length=20, verbose_name='待办类型'),
        ),
        migrations.AddField(
            model_name='todo',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='todos', to=settings.AUTH_USER_MODEL, verbose_name='所属用户'),
        ),
    ]
