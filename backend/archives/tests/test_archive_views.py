from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from archives.models import Archive, ArchiveLog, Todo, Category
from .base import BaseTestSetup


class ArchiveViewSetTests(APITestCase, BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('archive-list')
        self.detail_url = lambda pk: reverse('archive-detail', args=[pk])

    def test_list_archives_admin(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Archive.objects.count())

    def test_list_archives_entry_user(self):
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for archive in response.data['results']:
            self.assertEqual(archive['created_by'], self.entry_user.id)

    def test_list_archives_review_user(self):
        self.client.force_authenticate(user=self.review_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Archive.objects.count())

    def test_list_archives_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list_archives_no_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_archive_admin(self):
        response = self.client.get(self.detail_url(self.archive1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '测试案卷1')

    def test_retrieve_archive_entry_user_own(self):
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.detail_url(self.archive1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_archive_creates_log(self):
        log_count = ArchiveLog.objects.filter(archive=self.archive1, action_type='view').count()
        self.client.get(self.detail_url(self.archive1.id))
        self.assertEqual(
            ArchiveLog.objects.filter(archive=self.archive1, action_type='view').count(),
            log_count + 1
        )

    def test_retrieve_nonexistent_archive(self):
        response = self.client.get(self.detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_archive_admin(self):
        data = {
            'title': '新创建的案卷',
            'description': '案卷描述',
            'archive_number': 'ARCH-CREATE-TEST',
            'category': self.category_child.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        archive = Archive.objects.get(archive_number='ARCH-CREATE-TEST')
        self.assertEqual(archive.created_by, self.admin_user)
        self.assertEqual(archive.status, 'draft')

    def test_create_archive_entry_user(self):
        self.client.force_authenticate(user=self.entry_user)
        data = {
            'title': '录入用户创建的案卷',
            'description': '描述',
            'archive_number': 'ARCH-ENTRY-CREATE',
            'category': self.category_child.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        archive = Archive.objects.get(archive_number='ARCH-ENTRY-CREATE')
        self.assertEqual(archive.created_by, self.entry_user)

    def test_create_archive_creates_log(self):
        log_count = ArchiveLog.objects.count()
        data = {
            'title': '日志测试案卷',
            'description': '描述',
            'archive_number': 'ARCH-LOG-TEST',
            'category': self.category_child.id
        }
        self.client.post(self.list_url, data, format='json')
        self.assertEqual(ArchiveLog.objects.count(), log_count + 1)

    def test_create_archive_missing_required_fields(self):
        data = {'title': '缺少字段的案卷'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)
        self.assertIn('archive_number', response.data)
        self.assertIn('category', response.data)

    def test_create_archive_duplicate_number(self):
        data = {
            'title': '重复编号',
            'description': '描述',
            'archive_number': 'ARCH-001',
            'category': self.category_child.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('archive_number', response.data)

    def test_create_archive_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {
            'title': '普通用户创建',
            'description': '描述',
            'archive_number': 'ARCH-NORMAL-CREATE',
            'category': self.category_child.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        archive = Archive.objects.get(archive_number='ARCH-NORMAL-CREATE')
        self.assertEqual(archive.created_by, self.normal_user)

    def test_update_archive_admin(self):
        data = {
            'title': '更新后的标题',
            'description': '更新后的描述',
            'archive_number': 'ARCH-001',
            'category': self.category_child.id
        }
        response = self.client.put(self.detail_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.title, '更新后的标题')

    def test_update_archive_entry_user_draft(self):
        self.client.force_authenticate(user=self.entry_user)
        data = {
            'title': '草稿状态可以更新',
            'description': self.archive1.description,
            'archive_number': self.archive1.archive_number,
            'category': self.category_child.id
        }
        response = self.client.put(self.detail_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_archive_entry_user_pending_forbidden(self):
        self.client.force_authenticate(user=self.entry_user)
        data = {
            'title': '待审核不能更新',
            'description': self.archive2.description,
            'archive_number': self.archive2.archive_number,
            'category': self.category_child.id
        }
        response = self.client.put(self.detail_url(self.archive2.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_archive_entry_user_cannot_change_status(self):
        self.client.force_authenticate(user=self.entry_user)
        data = {
            'title': self.archive1.title,
            'description': self.archive1.description,
            'archive_number': self.archive1.archive_number,
            'category': self.category_child.id,
            'status': 'approved'
        }
        response = self.client.patch(self.detail_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.status, 'draft')

    def test_update_archive_creates_log(self):
        log_count = ArchiveLog.objects.filter(archive=self.archive1, action_type='update').count()
        data = {
            'title': '日志更新测试',
            'description': self.archive1.description,
            'archive_number': self.archive1.archive_number,
            'category': self.category_child.id
        }
        self.client.put(self.detail_url(self.archive1.id), data, format='json')
        self.assertEqual(
            ArchiveLog.objects.filter(archive=self.archive1, action_type='update').count(),
            log_count + 1
        )

    def test_partial_update_archive(self):
        data = {'description': '仅更新描述'}
        response = self.client.patch(self.detail_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.description, '仅更新描述')

    def test_update_nonexistent_archive(self):
        response = self.client.put(self.detail_url(99999), {
            'title': 'test', 'description': 'test',
            'archive_number': 'test', 'category': self.category_child.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_archive_admin(self):
        archive_id = self.archive1.id
        log_count_before = ArchiveLog.objects.count()
        response = self.client.delete(self.detail_url(archive_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Archive.objects.filter(id=archive_id).exists())
        self.assertEqual(ArchiveLog.objects.count(), log_count_before + 1)

    def test_delete_archive_entry_user_forbidden(self):
        self.client.force_authenticate(user=self.entry_user)
        archive_id = self.archive1.id
        response = self.client.delete(self.detail_url(archive_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Archive.objects.filter(id=archive_id).exists())

    def test_delete_archive_review_user_allowed(self):
        self.client.force_authenticate(user=self.review_user)
        archive_id = self.archive1.id
        log_count_before = ArchiveLog.objects.count()
        response = self.client.delete(self.detail_url(archive_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Archive.objects.filter(id=archive_id).exists())
        self.assertEqual(ArchiveLog.objects.count(), log_count_before + 1)

    def test_delete_nonexistent_archive(self):
        response = self.client.delete(self.detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_submit_for_review_draft(self):
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.status, 'pending')
        self.assertIsNotNone(self.archive1.submitted_at)

    def test_submit_for_review_rejected(self):
        self.archive1.status = 'rejected'
        self.archive1.save()
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive1.refresh_from_db()
        self.assertEqual(self.archive1.status, 'pending')

    def test_submit_for_review_pending_forbidden(self):
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-submit-for-review', args=[self.archive2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_for_review_approved_forbidden(self):
        self.archive1.status = 'approved'
        self.archive1.save()
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_for_review_not_owner_404(self):
        other_entry = self.entry_user.__class__.objects.create_user(
            username='other_entry', password='test12345', email='other@example.com'
        )
        other_entry.groups.add(self.entry_group)
        self.client.force_authenticate(user=other_entry)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_submit_for_review_normal_user_404(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_submit_for_review_creates_todos_for_reviewers(self):
        todo_count = Todo.objects.filter(archive=self.archive1, todo_type='review').count()
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-submit-for-review', args=[self.archive1.id])
        self.client.post(url)
        self.assertEqual(
            Todo.objects.filter(archive=self.archive1, todo_type='review').count(),
            todo_count + 1
        )

    def test_approve_archive(self):
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-approve', args=[self.archive2.id])
        data = {'comment': '审核通过'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive2.refresh_from_db()
        self.assertEqual(self.archive2.status, 'approved')
        self.assertEqual(self.archive2.reviewed_by, self.review_user)
        self.assertIsNotNone(self.archive2.reviewed_at)
        self.assertEqual(self.archive2.review_comment, '审核通过')

    def test_approve_archive_not_pending(self):
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-approve', args=[self.archive1.id])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_archive_no_permission(self):
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-approve', args=[self.archive2.id])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_archive_creates_notification(self):
        todo_count = Todo.objects.filter(archive=self.archive2, todo_type='notification').count()
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-approve', args=[self.archive2.id])
        self.client.post(url, {'comment': '通过'}, format='json')
        self.assertEqual(
            Todo.objects.filter(archive=self.archive2, todo_type='notification').count(),
            todo_count + 1
        )

    def test_reject_archive(self):
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-reject', args=[self.archive2.id])
        data = {'comment': '需要补充更多信息'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.archive2.refresh_from_db()
        self.assertEqual(self.archive2.status, 'rejected')
        self.assertEqual(self.archive2.reviewed_by, self.review_user)
        self.assertEqual(self.archive2.review_comment, '需要补充更多信息')

    def test_reject_archive_missing_comment(self):
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-reject', args=[self.archive2.id])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_archive_not_pending(self):
        self.client.force_authenticate(user=self.review_user)
        url = reverse('archive-reject', args=[self.archive1.id])
        response = self.client.post(url, {'comment': '驳回'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_archive_no_permission(self):
        self.client.force_authenticate(user=self.entry_user)
        url = reverse('archive-reject', args=[self.archive2.id])
        response = self.client.post(url, {'comment': '驳回'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_category(self):
        response = self.client.get(self.list_url, {'category': self.category_child.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for archive in response.data['results']:
            self.assertEqual(archive['category'], self.category_child.id)

    def test_filter_by_status(self):
        response = self.client.get(self.list_url, {'status': 'draft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for archive in response.data['results']:
            self.assertEqual(archive['status'], 'draft')

    def test_search_by_title(self):
        response = self.client.get(self.list_url, {'search': '案卷1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_search_by_archive_number(self):
        response = self.client.get(self.list_url, {'search': 'ARCH-001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_ordering_by_created_at_desc(self):
        response = self.client.get(self.list_url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [item['created_at'] for item in response.data['results']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_ordering_by_archive_number(self):
        response = self.client.get(self.list_url, {'ordering': 'archive_number'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numbers = [item['archive_number'] for item in response.data['results']]
        self.assertEqual(numbers, sorted(numbers))

    def test_pagination(self):
        for i in range(25):
            Archive.objects.create(
                title=f'分页测试案卷{i}',
                description='描述',
                archive_number=f'ARCH-PAGE-{i}',
                category=self.category_child
            )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_export_archives(self):
        url = reverse('archive-export')
        data = {'ids': [self.archive1.id, self.archive2.id], 'format': 'xlsx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_archives_no_ids(self):
        url = reverse('archive-export')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_archives_invalid_format(self):
        url = reverse('archive-export')
        data = {'ids': [self.archive1.id], 'format': 'invalid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_archives_empty_ids(self):
        url = reverse('archive-export')
        data = {'ids': [], 'format': 'xlsx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_archives_nonexistent_ids(self):
        url = reverse('archive-export')
        data = {'ids': [99999, 88888], 'format': 'xlsx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_archives_string_ids(self):
        url = reverse('archive-export')
        data = {'ids': f'{self.archive1.id},{self.archive2.id}', 'format': 'xlsx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
