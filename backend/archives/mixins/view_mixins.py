from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from ..models import ArchiveLog, ArchiveVersion, Todo, RejectRecord
from ..permissions import is_archive_entry_user, is_archive_review_user


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def create_archive_log(request, archive, action_type, old_data=None, new_data=None):
    operator = request.user.username if request.user.is_authenticated else 'anonymous'
    ip_address = get_client_ip(request)

    change_content = None
    if old_data is not None or new_data is not None:
        change_content = {
            'old': old_data,
            'new': new_data
        }

    return ArchiveLog.objects.create(
        archive=archive,
        archive_number=archive.archive_number if archive else '',
        archive_title=archive.title if archive else '',
        action_type=action_type,
        operator=operator,
        ip_address=ip_address,
        change_content=change_content
    )


def create_review_todos_for_archive(archive, group_name, created_by_username=''):
    try:
        review_group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return

    for user in review_group.user_set.all():
        Todo.objects.create(
            title=f'案卷待审核：{archive.archive_number}',
            description=f'案卷「{archive.title}」已提交审核，请及时处理。\n提交人：{created_by_username}',
            priority='high',
            status='pending',
            todo_type='review',
            is_read=False,
            user=user,
            archive=archive
        )


def create_notification_for_creator(archive, action, comment=''):
    if not archive.created_by:
        return

    action_text = {
        'approved': '审核通过',
        'rejected': '审核驳回',
    }.get(action, '审核完成')

    description = f'您的案卷「{archive.title}」已{action_text}。'
    if comment:
        description += f'\n审核意见：{comment}'

    Todo.objects.create(
        title=f'案卷{action_text}：{archive.archive_number}',
        description=description,
        priority='medium',
        status='pending',
        todo_type='notification',
        is_read=False,
        user=archive.created_by,
        archive=archive
    )


class ArchivePermissionMixin:
    def check_archive_permission(self, archive, user, permission_type):
        if user.is_staff:
            return True

        if permission_type == 'submit':
            if not is_archive_entry_user(user) and not user.is_staff:
                raise PermissionDenied('您没有提交审核的权限')
            if is_archive_entry_user(user) and archive.created_by != user:
                raise PermissionDenied('只能提交自己创建的案卷')

        elif permission_type == 'review':
            if not is_archive_review_user(user) and not user.is_staff:
                raise PermissionDenied('您没有审核权限')

        elif permission_type == 'view_versions':
            if not user.is_staff and not is_archive_review_user(user):
                if is_archive_entry_user(user) and archive.created_by != user:
                    raise PermissionDenied('您没有权限查看该案卷的版本记录')

        elif permission_type == 'rollback':
            if not user.is_staff and not is_archive_review_user(user):
                raise PermissionDenied('您没有权限回滚案卷版本')

        return True

    def check_archive_status(self, archive, allowed_statuses, error_message):
        if archive.status not in allowed_statuses:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(error_message)


class ArchiveOperationMixin:
    def get_old_data(self, instance):
        return instance.to_dict()

    def create_snapshot_and_log(self, request, archive, action_type, change_reason='', old_data=None):
        user = request.user if request.user.is_authenticated else None
        new_data = self.get_old_data(archive)

        if old_data is None:
            old_data = new_data

        create_archive_log(request, archive, action_type, old_data=old_data, new_data=new_data)
        ArchiveVersion.create_snapshot(archive, user, change_reason)

        return old_data, new_data

    def update_archive_status(self, archive, new_status, **kwargs):
        old_data = self.get_old_data(archive)
        archive.status = new_status

        for key, value in kwargs.items():
            setattr(archive, key, value)

        archive.save()
        return old_data, self.get_old_data(archive)

    def handle_reject_record(self, archive, rejected_by, reject_comment, old_data, new_data):
        return RejectRecord.create_reject_record(
            archive, rejected_by, reject_comment, old_data, new_data
        )

    def mark_resubmitted_records(self, archive):
        RejectRecord.objects.filter(
            archive=archive,
            is_resubmitted=False
        ).update(
            is_resubmitted=True,
            resubmitted_at=timezone.now()
        )
