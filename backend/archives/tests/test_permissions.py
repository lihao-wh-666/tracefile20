from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from archives.permissions import (
    is_user_in_group, is_archive_entry_user, is_archive_review_user,
    get_archive_entry_group, get_archive_review_group, setup_archive_groups,
    IsArchiveEntryUser, IsArchiveReviewUser, IsArchiveOwnerOrReviewer,
    ARCHIVE_ENTRY_GROUP_NAME, ARCHIVE_REVIEW_GROUP_NAME
)
from archives.models import Archive
from .base import BaseTestSetup
from rest_framework.test import APIRequestFactory


class PermissionHelperTests(BaseTestSetup):
    def test_is_user_in_group_true(self):
        self.assertTrue(is_user_in_group(self.entry_user, ARCHIVE_ENTRY_GROUP_NAME))
        self.assertTrue(is_user_in_group(self.review_user, ARCHIVE_REVIEW_GROUP_NAME))

    def test_is_user_in_group_false(self):
        self.assertFalse(is_user_in_group(self.normal_user, ARCHIVE_ENTRY_GROUP_NAME))
        self.assertFalse(is_user_in_group(self.entry_user, ARCHIVE_REVIEW_GROUP_NAME))

    def test_is_user_in_group_anonymous(self):
        self.assertFalse(is_user_in_group(None, ARCHIVE_ENTRY_GROUP_NAME))

    def test_is_user_in_group_unauthenticated(self):
        from django.contrib.auth.models import AnonymousUser
        anonymous = AnonymousUser()
        self.assertFalse(is_user_in_group(anonymous, ARCHIVE_ENTRY_GROUP_NAME))

    def test_is_archive_entry_user(self):
        self.assertTrue(is_archive_entry_user(self.entry_user))
        self.assertFalse(is_archive_entry_user(self.review_user))
        self.assertFalse(is_archive_entry_user(self.normal_user))

    def test_is_archive_review_user(self):
        self.assertTrue(is_archive_review_user(self.review_user))
        self.assertFalse(is_archive_review_user(self.entry_user))
        self.assertFalse(is_archive_review_user(self.normal_user))

    def test_get_archive_entry_group(self):
        group = get_archive_entry_group()
        self.assertEqual(group.name, ARCHIVE_ENTRY_GROUP_NAME)
        self.assertTrue(Group.objects.filter(name=ARCHIVE_ENTRY_GROUP_NAME).exists())

    def test_get_archive_review_group(self):
        group = get_archive_review_group()
        self.assertEqual(group.name, ARCHIVE_REVIEW_GROUP_NAME)
        self.assertTrue(Group.objects.filter(name=ARCHIVE_REVIEW_GROUP_NAME).exists())

    def test_setup_archive_groups(self):
        Group.objects.all().delete()
        entry_group, review_group = setup_archive_groups()
        self.assertEqual(entry_group.name, ARCHIVE_ENTRY_GROUP_NAME)
        self.assertEqual(review_group.name, ARCHIVE_REVIEW_GROUP_NAME)

        content_type = ContentType.objects.get_for_model(Archive)
        add_perm = Permission.objects.get(content_type=content_type, codename='add_archive')
        change_perm = Permission.objects.get(content_type=content_type, codename='change_archive')
        view_perm = Permission.objects.get(content_type=content_type, codename='view_archive')
        delete_perm = Permission.objects.get(content_type=content_type, codename='delete_archive')

        self.assertIn(add_perm, entry_group.permissions.all())
        self.assertIn(change_perm, entry_group.permissions.all())
        self.assertIn(view_perm, entry_group.permissions.all())
        self.assertNotIn(delete_perm, entry_group.permissions.all())

        self.assertIn(view_perm, review_group.permissions.all())
        self.assertIn(change_perm, review_group.permissions.all())
        self.assertNotIn(add_perm, review_group.permissions.all())
        self.assertNotIn(delete_perm, review_group.permissions.all())


class IsArchiveEntryUserTests(BaseTestSetup):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsArchiveEntryUser()

    def test_has_permission_entry_user(self):
        request = self.factory.get('/')
        request.user = self.entry_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_admin(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_normal_user(self):
        request = self.factory.get('/')
        request.user = self.normal_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_review_user(self):
        request = self.factory.get('/')
        request.user = self.review_user
        self.assertFalse(self.permission.has_permission(request, None))


class IsArchiveReviewUserTests(BaseTestSetup):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsArchiveReviewUser()

    def test_has_permission_review_user(self):
        request = self.factory.get('/')
        request.user = self.review_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_admin(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_normal_user(self):
        request = self.factory.get('/')
        request.user = self.normal_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_entry_user(self):
        request = self.factory.get('/')
        request.user = self.entry_user
        self.assertFalse(self.permission.has_permission(request, None))


class IsArchiveOwnerOrReviewerTests(BaseTestSetup):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsArchiveOwnerOrReviewer()

    def test_has_object_permission_admin(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(self.permission.has_object_permission(request, None, self.archive1))

    def test_has_object_permission_reviewer(self):
        request = self.factory.get('/')
        request.user = self.review_user
        self.assertTrue(self.permission.has_object_permission(request, None, self.archive1))

    def test_has_object_permission_owner(self):
        request = self.factory.get('/')
        request.user = self.entry_user
        self.assertTrue(self.permission.has_object_permission(request, None, self.archive1))

    def test_has_object_permission_not_owner(self):
        other_entry = User.objects.create_user(
            username='other_entry2', password='test12345', email='other2@example.com'
        )
        other_entry.groups.add(self.entry_group)
        request = self.factory.get('/')
        request.user = other_entry
        self.assertFalse(self.permission.has_object_permission(request, None, self.archive1))

    def test_has_object_permission_normal_user(self):
        request = self.factory.get('/')
        request.user = self.normal_user
        self.assertFalse(self.permission.has_object_permission(request, None, self.archive1))
