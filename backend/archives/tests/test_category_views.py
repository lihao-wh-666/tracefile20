from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from archives.models import Category
from .base import BaseTestSetup


class CategoryViewSetTests(APITestCase, BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('category-list')
        self.detail_url = lambda pk: reverse('category-detail', args=[pk])

    def test_list_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Category.objects.count())

    def test_retrieve_category(self):
        response = self.client.get(self.detail_url(self.category_root.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '档案分类')
        self.assertEqual(len(response.data['children']), 2)

    def test_create_category(self):
        data = {
            'name': '新分类',
            'description': '新创建的分类'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='新分类').exists())

    def test_create_category_with_parent(self):
        data = {
            'name': '孙分类',
            'description': '三级分类',
            'parent': self.category_child.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(name='孙分类').parent_id, self.category_child.id)

    def test_create_category_missing_name(self):
        data = {'description': '没有名称的分类'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_category_empty_name(self):
        data = {'name': '', 'description': '空名称'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category(self):
        data = {
            'name': '更新后的分类',
            'description': '描述已更新'
        }
        response = self.client.put(self.detail_url(self.category_child.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_child.refresh_from_db()
        self.assertEqual(self.category_child.name, '更新后的分类')

    def test_partial_update_category(self):
        data = {'description': '仅更新描述'}
        response = self.client.patch(self.detail_url(self.category_child.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category_child.refresh_from_db()
        self.assertEqual(self.category_child.description, '仅更新描述')

    def test_delete_category(self):
        category_id = self.category_second_child.id
        response = self.client.delete(self.detail_url(category_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category_id).exists())

    def test_delete_category_with_children(self):
        root_id = self.category_root.id
        child_id = self.category_child.id
        response = self.client.delete(self.detail_url(root_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=root_id).exists())
        self.assertFalse(Category.objects.filter(id=child_id).exists())

    def test_tree_view(self):
        url = reverse('category-tree')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], '档案分类')
        self.assertEqual(len(response.data[0]['children']), 2)

    def test_simple_list_view(self):
        url = reverse('category-simple')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Category.objects.count())
        for item in response.data:
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertEqual(len(item.keys()), 2)

    def test_search_categories(self):
        response = self.client.get(self.list_url, {'search': '人事'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_no_results(self):
        response = self.client.get(self.list_url, {'search': '不存在的关键词'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_ordering_by_name(self):
        response = self.client.get(self.list_url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_ordering_by_created_at_desc(self):
        response = self.client.get(self.list_url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [item['created_at'] for item in response.data['results']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_retrieve_nonexistent_category(self):
        url = self.detail_url(99999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_category(self):
        url = self.detail_url(99999)
        response = self.client.put(url, {'name': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_category(self):
        url = self.detail_url(99999)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pagination(self):
        for i in range(25):
            Category.objects.create(name=f'分页测试分类{i}')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_category_permissions_no_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
