from django.test import TestCase
from archives.serializers import ArchiveSerializer
from archives.models import Archive, Category
from .base import BaseTestSetup


class ArchiveSerializerTests(BaseTestSetup):
    def test_archive_serializer_valid_data(self):
        data = {
            'title': '有效案卷',
            'description': '有效描述',
            'archive_number': 'ARCH-VALID',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_archive_serializer_missing_title(self):
        data = {
            'description': '描述',
            'archive_number': 'ARCH-MISSING-TITLE',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_archive_serializer_missing_description(self):
        data = {
            'title': '案卷',
            'archive_number': 'ARCH-MISSING-DESC',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_archive_serializer_missing_archive_number(self):
        data = {
            'title': '案卷',
            'description': '描述',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('archive_number', serializer.errors)

    def test_archive_serializer_missing_category(self):
        data = {
            'title': '案卷',
            'description': '描述',
            'archive_number': 'ARCH-MISSING-CAT'
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)

    def test_archive_serializer_empty_title(self):
        data = {
            'title': '',
            'description': '描述',
            'archive_number': 'ARCH-EMPTY-TITLE',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_archive_serializer_invalid_category(self):
        data = {
            'title': '案卷',
            'description': '描述',
            'archive_number': 'ARCH-INVALID-CAT',
            'category': 99999
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)

    def test_archive_serializer_title_too_long(self):
        data = {
            'title': 'a' * 201,
            'description': '描述',
            'archive_number': 'ARCH-LONG-TITLE',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_archive_serializer_archive_number_too_long(self):
        data = {
            'title': '案卷',
            'description': '描述',
            'archive_number': 'A' * 101,
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('archive_number', serializer.errors)

    def test_archive_serializer_read_only_fields(self):
        data = {
            'title': '测试只读字段',
            'description': '描述',
            'archive_number': 'ARCH-READONLY',
            'category': self.category_child.id,
            'created_by': self.normal_user.id,
            'reviewed_by': self.review_user.id,
            'reviewed_at': '2024-01-01T00:00:00Z',
            'submitted_at': '2024-01-01T00:00:00Z',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        serializer = ArchiveSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertNotEqual(instance.created_at.isoformat(), '2024-01-01T00:00:00Z')

    def test_archive_serializer_category_name(self):
        serializer = ArchiveSerializer(instance=self.archive1)
        data = serializer.data
        self.assertEqual(data['category_name'], '人事档案')

    def test_archive_serializer_status_display(self):
        serializer = ArchiveSerializer(instance=self.archive1)
        data = serializer.data
        self.assertEqual(data['status_display'], '草稿')

    def test_archive_serializer_created_by_username(self):
        serializer = ArchiveSerializer(instance=self.archive1)
        data = serializer.data
        self.assertEqual(data['created_by_username'], 'entry_user')

    def test_archive_serializer_reviewed_by_username_none(self):
        serializer = ArchiveSerializer(instance=self.archive1)
        data = serializer.data
        self.assertIsNone(data['reviewed_by_username'])

    def test_archive_serializer_reviewed_by_username(self):
        self.archive2.reviewed_by = self.review_user
        self.archive2.save()
        serializer = ArchiveSerializer(instance=self.archive2)
        data = serializer.data
        self.assertEqual(data['reviewed_by_username'], 'review_user')

    def test_archive_serializer_update(self):
        data = {
            'title': '更新标题',
            'description': '更新描述',
            'archive_number': self.archive1.archive_number,
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(instance=self.archive1, data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.title, '更新标题')
        self.assertEqual(instance.description, '更新描述')

    def test_archive_serializer_partial_update(self):
        data = {'description': '只更新描述'}
        serializer = ArchiveSerializer(instance=self.archive1, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.title, '测试案卷1')
        self.assertEqual(instance.description, '只更新描述')

    def test_archive_serializer_create(self):
        data = {
            'title': '序列化器创建',
            'description': '描述',
            'archive_number': 'ARCH-SERIALIZER-CREATE',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertTrue(Archive.objects.filter(id=instance.id).exists())
        self.assertEqual(instance.status, 'draft')

    def test_archive_serializer_duplicate_archive_number(self):
        data = {
            'title': '重复编号',
            'description': '描述',
            'archive_number': 'ARCH-001',
            'category': self.category_child.id
        }
        serializer = ArchiveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('archive_number', serializer.errors)

    def test_archive_serializer_contains_all_fields(self):
        serializer = ArchiveSerializer(instance=self.archive1)
        expected_fields = [
            'id', 'title', 'description', 'archive_number',
            'category', 'category_name', 'status', 'status_display',
            'created_at', 'updated_at', 'created_by', 'created_by_username',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'review_comment',
            'submitted_at'
        ]
        for field in expected_fields:
            self.assertIn(field, serializer.data)
