from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from archives.models import Archive, Category, ArchiveLog, Todo
from .base import BaseTestSetup


class ArchiveModelTests(BaseTestSetup):
    def test_archive_creation(self):
        archive = Archive.objects.create(
            title='新建案卷',
            description='案卷描述',
            archive_number='ARCH-NEW-001',
            category=self.category_child,
            created_by=self.entry_user
        )
        self.assertEqual(archive.title, '新建案卷')
        self.assertEqual(archive.status, 'draft')
        self.assertEqual(archive.created_by, self.entry_user)
        self.assertIsNotNone(archive.created_at)

    def test_archive_default_status(self):
        archive = Archive.objects.create(
            title='默认状态案卷',
            description='描述',
            archive_number='ARCH-DEFAULT',
            category=self.category_child
        )
        self.assertEqual(archive.status, 'draft')

    def test_archive_status_choices(self):
        for status_val, _ in Archive.STATUS_CHOICES:
            archive = Archive(
                title=f'状态{status_val}',
                description='描述',
                archive_number=f'ARCH-STATUS-{status_val}',
                category=self.category_child,
                status=status_val
            )
            archive.full_clean()
            archive.save()
            self.assertEqual(archive.status, status_val)

    def test_archive_str_method(self):
        expected = f'{self.archive1.archive_number} - {self.archive1.title}'
        self.assertEqual(str(self.archive1), expected)

    def test_archive_ordering(self):
        archives = list(Archive.objects.all())
        self.assertGreaterEqual(archives[0].created_at, archives[-1].created_at)

    def test_archive_unique_archive_number(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Archive.objects.create(
                title='重复编号案卷',
                description='描述',
                archive_number='ARCH-001',
                category=self.category_child
            )

    def test_archive_category_relationship(self):
        self.assertEqual(self.archive1.category, self.category_child)
        self.assertIn(self.archive1, self.category_child.archives.all())

    def test_archive_created_by_relationship(self):
        self.assertEqual(self.archive1.created_by, self.entry_user)
        self.assertIn(self.archive1, self.entry_user.created_archives.all())

    def test_archive_reviewed_by_relationship(self):
        self.archive1.reviewed_by = self.review_user
        self.archive1.reviewed_at = timezone.now()
        self.archive1.save()
        self.assertEqual(self.archive1.reviewed_by, self.review_user)
        self.assertIn(self.archive1, self.review_user.reviewed_archives.all())

    def test_archive_null_created_by(self):
        archive = Archive.objects.create(
            title='无创建人案卷',
            description='描述',
            archive_number='ARCH-NULL-CREATOR',
            category=self.category_child,
            created_by=None
        )
        self.assertIsNone(archive.created_by)

    def test_archive_blank_description(self):
        archive = Archive.objects.create(
            title='无描述案卷',
            description='',
            archive_number='ARCH-BLANK-DESC',
            category=self.category_child
        )
        self.assertEqual(archive.description, '')

    def test_archive_update_timestamps(self):
        original_updated_at = self.archive1.updated_at
        self.archive1.title = '更新后的标题'
        self.archive1.save()
        self.archive1.refresh_from_db()
        self.assertGreaterEqual(self.archive1.updated_at, original_updated_at)

    def test_archive_review_fields(self):
        self.archive1.status = 'approved'
        self.archive1.reviewed_by = self.review_user
        self.archive1.reviewed_at = timezone.now()
        self.archive1.review_comment = '审核通过，内容符合规范'
        self.archive1.submitted_at = timezone.now()
        self.archive1.save()
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.status, 'approved')
        self.assertEqual(self.archive1.reviewed_by, self.review_user)
        self.assertIsNotNone(self.archive1.reviewed_at)
        self.assertEqual(self.archive1.review_comment, '审核通过，内容符合规范')
        self.assertIsNotNone(self.archive1.submitted_at)

    def test_archive_delete_cascade_category(self):
        category = Category.objects.create(name='即将删除的分类')
        archive = Archive.objects.create(
            title='关联分类案卷',
            description='描述',
            archive_number='ARCH-CASCADE-TEST',
            category=category
        )
        archive_id = archive.id
        category.delete()
        self.assertFalse(Archive.objects.filter(id=archive_id).exists())

    def test_archive_delete_set_null_created_by(self):
        user = User.objects.create_user(
            username='temp_user',
            password='test12345',
            email='temp@example.com'
        )
        archive = Archive.objects.create(
            title='临时用户案卷',
            description='描述',
            archive_number='ARCH-SET-NULL',
            category=self.category_child,
            created_by=user
        )
        archive_id = archive.id
        user.delete()
        archive.refresh_from_db()
        self.assertTrue(Archive.objects.filter(id=archive_id).exists())
        self.assertIsNone(archive.created_by)

    def test_archive_related_logs(self):
        log = ArchiveLog.objects.create(
            archive=self.archive1,
            archive_number=self.archive1.archive_number,
            archive_title=self.archive1.title,
            action_type='create',
            operator='testuser',
            ip_address='127.0.0.1'
        )
        self.assertIn(log, self.archive1.logs.all())

    def test_archive_related_todos(self):
        todo = Todo.objects.create(
            title='测试待办',
            archive=self.archive1,
            user=self.review_user
        )
        self.assertIn(todo, self.archive1.todos.all())

    def test_archive_title_max_length(self):
        long_title = 'a' * 200
        archive = Archive.objects.create(
            title=long_title,
            description='描述',
            archive_number='ARCH-LONG-TITLE',
            category=self.category_child
        )
        self.assertEqual(len(archive.title), 200)

    def test_archive_archive_number_max_length(self):
        long_number = 'A' * 100
        archive = Archive.objects.create(
            title='案卷',
            description='描述',
            archive_number=long_number,
            category=self.category_child
        )
        self.assertEqual(len(archive.archive_number), 100)
