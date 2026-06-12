from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions


ARCHIVE_ENTRY_GROUP_NAME = '案卷管理录入组'
ARCHIVE_REVIEW_GROUP_NAME = '案卷管理审核组'


def is_user_in_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


def is_archive_entry_user(user):
    return is_user_in_group(user, ARCHIVE_ENTRY_GROUP_NAME)


def is_archive_review_user(user):
    return is_user_in_group(user, ARCHIVE_REVIEW_GROUP_NAME)


def get_or_create_group(group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    return group


def get_archive_entry_group():
    return get_or_create_group(ARCHIVE_ENTRY_GROUP_NAME)


def get_archive_review_group():
    return get_or_create_group(ARCHIVE_REVIEW_GROUP_NAME)


def get_archive_permissions():
    from .models import Archive
    content_type = ContentType.objects.get_for_model(Archive)
    return {
        'add': Permission.objects.get(content_type=content_type, codename='add_archive'),
        'change': Permission.objects.get(content_type=content_type, codename='change_archive'),
        'view': Permission.objects.get(content_type=content_type, codename='view_archive'),
        'delete': Permission.objects.get(content_type=content_type, codename='delete_archive'),
    }


def setup_archive_groups():
    entry_group = get_archive_entry_group()
    review_group = get_archive_review_group()

    permissions = get_archive_permissions()

    entry_group.permissions.add(
        permissions['add'],
        permissions['change'],
        permissions['view']
    )

    review_group.permissions.add(
        permissions['view'],
        permissions['change']
    )

    return entry_group, review_group


class BaseGroupPermission(permissions.BasePermission):
    group_name = None

    def has_permission(self, request, view):
        return is_user_in_group(request.user, self.group_name) or request.user.is_staff


class IsArchiveEntryUser(BaseGroupPermission):
    group_name = ARCHIVE_ENTRY_GROUP_NAME


class IsArchiveReviewUser(BaseGroupPermission):
    group_name = ARCHIVE_REVIEW_GROUP_NAME


class IsArchiveOwnerOrReviewer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or is_archive_review_user(request.user):
            return True
        if is_archive_entry_user(request.user):
            return obj.created_by == request.user
        return False
