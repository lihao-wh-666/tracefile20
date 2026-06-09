from django.test import TestCase
from archives.serializers import CategorySerializer, CategorySimpleSerializer
from archives.models import Category
from .base import BaseTestSetup


class CategorySerializerTests(BaseTestSetup):
    def test_category_serializer_valid_data(self):
        data = {
            'name': '有效分类',
            'description': '有效描述'
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_category_serializer_missing_name(self):
        data = {'description': '缺少名称'}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_category_serializer_empty_name(self):
        data = {'name': '', 'description': '空名称'}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_category_serializer_name_too_long(self):
        data = {'name': 'a' * 101}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_category_serializer_with_parent(self):
        data = {
            'name': '子分类',
            'description': '子分类描述',
            'parent': self.category_root.id
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_category_serializer_invalid_parent(self):
        data = {
            'name': '子分类',
            'parent': 99999
        }
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)

    def test_category_serializer_read_only_fields(self):
        data = {
            'name': '测试',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertNotEqual(instance.created_at.isoformat(), '2024-01-01T00:00:00Z')

    def test_category_serializer_children_nested(self):
        serializer = CategorySerializer(instance=self.category_root)
        data = serializer.data
        self.assertIn('children', data)
        self.assertEqual(len(data['children']), 2)
        for child in data['children']:
            self.assertIn('children', child)

    def test_category_serializer_parent_name(self):
        serializer = CategorySerializer(instance=self.category_child)
        data = serializer.data
        self.assertEqual(data['parent_name'], '档案分类')

    def test_category_serializer_no_parent_name(self):
        serializer = CategorySerializer(instance=self.category_root)
        data = serializer.data
        self.assertIsNone(data['parent_name'])

    def test_category_simple_serializer(self):
        serializer = CategorySimpleSerializer(instance=self.category_root)
        data = serializer.data
        self.assertEqual(set(data.keys()), {'id', 'name'})

    def test_category_simple_serializer_list(self):
        categories = Category.objects.all()
        serializer = CategorySimpleSerializer(categories, many=True)
        self.assertEqual(len(serializer.data), categories.count())

    def test_category_serializer_update(self):
        data = {'name': '更新名称', 'description': '更新描述'}
        serializer = CategorySerializer(instance=self.category_child, data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.name, '更新名称')
        self.assertEqual(instance.description, '更新描述')

    def test_category_serializer_partial_update(self):
        data = {'description': '只更新描述'}
        serializer = CategorySerializer(instance=self.category_child, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.name, '人事档案')
        self.assertEqual(instance.description, '只更新描述')

    def test_category_serializer_create(self):
        data = {'name': '新创建的分类', 'description': '描述'}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertTrue(Category.objects.filter(id=instance.id).exists())

    def test_category_serializer_blank_description(self):
        data = {'name': '无描述分类'}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.description, '')
