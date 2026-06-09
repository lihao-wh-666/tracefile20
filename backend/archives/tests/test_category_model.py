from django.test import TestCase
from archives.models import Category, Archive
from django.contrib.auth.models import User
from django.utils import timezone
from .base import BaseTestSetup


class CategoryModelTests(BaseTestSetup):
    def test_category_creation(self):
        category = Category.objects.create(
            name='测试分类',
            description='这是一个测试分类'
        )
        self.assertEqual(category.name, '测试分类')
        self.assertEqual(category.description, '这是一个测试分类')
        self.assertIsNone(category.parent)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_category_with_parent(self):
        category = Category.objects.create(
            name='子分类',
            description='子分类描述',
            parent=self.category_root
        )
        self.assertEqual(category.parent, self.category_root)
        self.assertIn(category, self.category_root.children.all())

    def test_category_str_method(self):
        self.assertEqual(str(self.category_root), '档案分类')
        self.assertEqual(str(self.category_child), '人事档案')

    def test_category_ordering(self):
        Category.objects.create(name='ZZ分类')
        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, 'ZZ分类')

    def test_nested_categories(self):
        sub_child = Category.objects.create(
            name='员工档案',
            parent=self.category_child
        )
        self.assertEqual(sub_child.parent, self.category_child)
        self.assertEqual(sub_child.parent.parent, self.category_root)

    def test_category_delete_cascade(self):
        parent_id = self.category_root.id
        child_id = self.category_child.id
        self.category_root.delete()
        self.assertFalse(Category.objects.filter(id=parent_id).exists())
        self.assertFalse(Category.objects.filter(id=child_id).exists())

    def test_category_name_max_length(self):
        long_name = 'a' * 100
        category = Category.objects.create(name=long_name)
        self.assertEqual(len(category.name), 100)

    def test_blank_description(self):
        category = Category.objects.create(name='无描述分类')
        self.assertEqual(category.description, '')

    def test_category_update_timestamp(self):
        original_updated_at = self.category_root.updated_at
        self.category_root.name = '更新后的分类名称'
        self.category_root.save()
        self.category_root.refresh_from_db()
        self.assertGreaterEqual(self.category_root.updated_at, original_updated_at)

    def test_multiple_children_same_parent(self):
        child_count = self.category_root.children.count()
        self.assertEqual(child_count, 2)
        self.assertIn(self.category_child, self.category_root.children.all())
        self.assertIn(self.category_second_child, self.category_root.children.all())

    def test_category_related_archives(self):
        archive_count = self.category_child.archives.count()
        self.assertEqual(archive_count, 1)
        self.assertIn(self.archive1, self.category_child.archives.all())
