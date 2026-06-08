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


def get_archive_entry_group():
    group, created = Group.objects.get_or_create(name=ARCHIVE_ENTRY_GROUP_NAME)
    return group


def get_archive_review_group():
    group, created = Group.objects.get_or_create(name=ARCHIVE_REVIEW_GROUP_NAME)
    return group


def setup_archive_groups():
    from .models import Archive

    entry_group = get_archive_entry_group()
    review_group = get_archive_review_group()

    content_type = ContentType.objects.get_for_model(Archive)

    add_permission = Permission.objects.get(content_type=content_type, codename='add_archive')
    change_permission = Permission.objects.get(content_type=content_type, codename='change_archive')
    view_permission = Permission.objects.get(content_type=content_type, codename='view_archive')
    delete_permission = Permission.objects.get(content_type=content_type, codename='delete_archive')

    entry_group.permissions.add(add_permission, change_permission, view_permission)

    review_group.permissions.add(view_permission, change_permission)

    return entry_group, review_group


class IsArchiveEntryUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_archive_entry_user(request.user) or request.user.is_staff


class IsArchiveReviewUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_archive_review_user(request.user) or request.user.is_staff


class IsArchiveOwnerOrReviewer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if is_archive_review_user(request.user):
            return True
        if is_archive_entry_user(request.user):
            return obj.created_by == request.user
        return False
