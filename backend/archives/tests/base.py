from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from archives.models import Category, Archive, Todo, LoginAttempt, UserProfile, UserPreference, ArchiveLog
from archives.permissions import (
    setup_archive_groups, is_archive_entry_user, is_archive_review_user,
    ARCHIVE_ENTRY_GROUP_NAME, ARCHIVE_REVIEW_GROUP_NAME
)


class BaseTestSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_archive_groups()
        cls.entry_group = Group.objects.get(name=ARCHIVE_ENTRY_GROUP_NAME)
        cls.review_group = Group.objects.get(name=ARCHIVE_REVIEW_GROUP_NAME)

        cls.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )

        cls.entry_user = User.objects.create_user(
            username='entry_user',
            password='test12345',
            email='entry@example.com'
        )
        cls.entry_user.groups.add(cls.entry_group)

        cls.review_user = User.objects.create_user(
            username='review_user',
            password='test12345',
            email='review@example.com'
        )
        cls.review_user.groups.add(cls.review_group)

        cls.normal_user = User.objects.create_user(
            username='normal_user',
            password='test12345',
            email='normal@example.com'
        )

        cls.category_root = Category.objects.create(
            name='档案分类',
            description='根分类'
        )
        cls.category_child = Category.objects.create(
            name='人事档案',
            description='人事相关档案',
            parent=cls.category_root
        )
        cls.category_second_child = Category.objects.create(
            name='财务档案',
            description='财务相关档案',
            parent=cls.category_root
        )

        cls.archive1 = Archive.objects.create(
            title='测试案卷1',
            description='这是第一个测试案卷',
            archive_number='ARCH-001',
            category=cls.category_child,
            status='draft',
            created_by=cls.entry_user
        )
        cls.archive2 = Archive.objects.create(
            title='测试案卷2',
            description='这是第二个测试案卷',
            archive_number='ARCH-002',
            category=cls.category_second_child,
            status='pending',
            created_by=cls.entry_user
        )
