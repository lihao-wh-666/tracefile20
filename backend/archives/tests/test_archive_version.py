from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from archives.models import Archive, ArchiveVersion, RejectRecord, Category
from .base import BaseTestSetup


class ArchiveVersionModelTests(BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_create_snapshot_on_create(self):
        version_count = ArchiveVersion.objects.filter(archive=self.archive1).count()
        self.assertEqual(version_count, 1)
        version = ArchiveVersion.objects.filter(archive=self.archive1).first()
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.title, self.archive1.title)
        self.assertEqual(version.change_reason, '创建案卷')

    def test_create_snapshot_manual(self):
        version_count = ArchiveVersion.objects.filter(archive=self.archive1).count()
        ArchiveVersion.create_snapshot(self.archive1, self.admin_user, '手动测试快照')
        self.assertEqual(
            ArchiveVersion.objects.filter(archive=self.archive1).count(),
            version_count + 1
        )
        version = ArchiveVersion.objects.filter(archive=self.archive1).order_by('-version_number').first()
        self.assertEqual(version.version_number, version_count + 1)
        self.assertEqual(version.change_reason, '手动测试快照')
        self.assertEqual(version.created_by, self.admin_user)

    def test_restore_version(self):
        self.archive1.title = '修改后的标题'
        self.archive1.description = '修改后的描述'
        self.archive1.status = 'approved'
        self.archive1.save()
        ArchiveVersion.create_snapshot(self.archive1, self.admin_user, '修改案卷')

        first_version = ArchiveVersion.objects.get(archive=self.archive1, version_number=1)
        restored_archive, old_data, new_data = first_version.restore(self.admin_user)

        self.assertEqual(restored_archive.title, '测试案卷1')
        self.assertEqual(restored_archive.description, '这是第一个测试案卷')
        self.assertEqual(restored_archive.status, 'draft')
        self.assertIsNone(restored_archive.reviewed_by)
        self.assertIsNone(restored_archive.reviewed_at)
        self.assertEqual(restored_archive.review_comment, '')
        self.assertIsNone(restored_archive.submitted_at)

        new_version = ArchiveVersion.objects.filter(archive=self.archive1).order_by('-version_number').first()
        self.assertIn('回滚到版本1', new_version.change_reason)
        self.assertEqual(new_version.created_by, self.admin_user)

    def test_version_ordering(self):
        for i in range(3):
            self.archive1.title = f'标题{i}'
            self.archive1.save()
            ArchiveVersion.create_snapshot(self.archive1, self.admin_user, f'修改{i}')

        versions = ArchiveVersion.objects.filter(archive=self.archive1)
        numbers = [v.version_number for v in versions]
        self.assertEqual(numbers, sorted(numbers, reverse=True))


class RejectRecordModelTests(BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_create_reject_record(self):
        old_data = {
            'title': '原始标题',
            'description': '原始描述',
            'status': 'pending'
        }
        new_data = {
            'title': '原始标题',
            'description': '原始描述',
            'status': 'rejected'
        }

        reject_record = RejectRecord.create_reject_record(
            self.archive2, self.review_user, '需要补充更多信息',
            old_data, new_data
        )

        self.assertEqual(reject_record.archive, self.archive2)
        self.assertEqual(reject_record.rejected_by, self.review_user)
        self.assertEqual(reject_record.reject_comment, '需要补充更多信息')
        self.assertEqual(reject_record.data_before, old_data)
        self.assertEqual(reject_record.data_after, new_data)
        self.assertIn('status', reject_record.field_changes)
        self.assertEqual(reject_record.field_changes['status']['old'], 'pending')
        self.assertEqual(reject_record.field_changes['status']['new'], 'rejected')
        self.assertFalse(reject_record.is_resubmitted)
        self.assertIsNone(reject_record.resubmitted_at)

    def test_mark_resubmitted(self):
        old_data = {'status': 'pending'}
        new_data = {'status': 'rejected'}
        reject_record = RejectRecord.create_reject_record(
            self.archive2, self.review_user, '测试驳回', old_data, new_data
        )

        self.assertFalse(reject_record.is_resubmitted)
        reject_record.mark_resubmitted()
        reject_record.refresh_from_db()
        self.assertTrue(reject_record.is_resubmitted)
        self.assertIsNotNone(reject_record.resubmitted_at)


class ArchiveVersionViewSetTests(APITestCase, BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('archiveversion-list')
        self.detail_url = lambda pk: reverse('archiveversion-detail', args=[pk])

    def test_list_versions_admin(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], ArchiveVersion.objects.count())

    def test_list_versions_review_user(self):
        self.client.force_authenticate(user=self.review_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], ArchiveVersion.objects.count())

    def test_list_versions_entry_user_own(self):
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for version in response.data['results']:
            archive = Archive.objects.get(id=version['archive'])
            self.assertEqual(archive.created_by, self.entry_user)

    def test_list_versions_normal_user_empty(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list_versions_no_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_version(self):
        version = ArchiveVersion.objects.first()
        response = self.client.get(self.detail_url(version.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['version_number'], version.version_number)
        self.assertEqual(response.data['title'], version.title)

    def test_filter_by_archive(self):
        response = self.client.get(self.list_url, {'archive': self.archive1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for version in response.data['results']:
            self.assertEqual(version['archive'], self.archive1.id)

    def test_search_by_title(self):
        response = self.client.get(self.list_url, {'search': '测试案卷1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)


class RejectRecordViewSetTests(APITestCase, BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('rejectrecord-list')
        self.detail_url = lambda pk: reverse('rejectrecord-detail', args=[pk])

    def test_list_reject_records_admin(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], RejectRecord.objects.count())

    def test_list_reject_records_review_user(self):
        self.client.force_authenticate(user=self.review_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], RejectRecord.objects.count())

    def test_list_reject_records_entry_user_own(self):
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for record in response.data['results']:
            archive = Archive.objects.get(id=record['archive'])
            self.assertEqual(archive.created_by, self.entry_user)

    def test_list_reject_records_normal_user_empty(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_by_archive(self):
        old_data = {'status': 'pending'}
        new_data = {'status': 'rejected'}
        RejectRecord.create_reject_record(
            self.archive2, self.review_user, '测试驳回', old_data, new_data
        )
        response = self.client.get(self.list_url, {'archive': self.archive2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)


class ArchiveVersionIntegrationTests(APITestCase, BaseTestSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        self.archive_detail_url = lambda pk: reverse('archive-detail', args=[pk])
        self.versions_url = lambda pk: reverse('archive-versions', args=[pk])
        self.version_detail_url = lambda pk, version_id: reverse('archive-version-detail', args=[pk, version_id])
        self.rollback_url = lambda pk: reverse('archive-rollback', args=[pk])
        self.reject_records_url = lambda pk: reverse('archive-reject-records', args=[pk])
        self.submit_url = lambda pk: reverse('archive-submit-for-review', args=[pk])
        self.reject_url = lambda pk: reverse('archive-reject', args=[pk])

    def test_create_archive_creates_version(self):
        version_count_before = ArchiveVersion.objects.count()
        data = {
            'title': '新版本测试案卷',
            'description': '描述',
            'archive_number': 'ARCH-VERSION-TEST',
            'category': self.category_child.id
        }
        response = self.client.post(reverse('archive-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArchiveVersion.objects.count(), version_count_before + 1)

        archive = Archive.objects.get(archive_number='ARCH-VERSION-TEST')
        version = ArchiveVersion.objects.filter(archive=archive).first()
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.change_reason, '创建案卷')

    def test_update_archive_creates_version(self):
        archive = self.archive1
        version_count_before = ArchiveVersion.objects.filter(archive=archive).count()
        data = {
            'title': '更新后的标题',
            'description': archive.description,
            'archive_number': archive.archive_number,
            'category': self.category_child.id,
            'change_reason': '修改标题测试'
        }
        response = self.client.put(self.archive_detail_url(archive.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ArchiveVersion.objects.filter(archive=archive).count(),
            version_count_before + 1
        )

        latest_version = ArchiveVersion.objects.filter(archive=archive).order_by('-version_number').first()
        self.assertEqual(latest_version.change_reason, '修改标题测试')
        self.assertEqual(latest_version.title, '更新后的标题')

    def test_get_archive_versions(self):
        response = self.client.get(self.versions_url(self.archive1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_archive_version_detail(self):
        version = ArchiveVersion.objects.filter(archive=self.archive1).first()
        response = self.client.get(self.version_detail_url(self.archive1.id, version.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], version.id)
        self.assertEqual(response.data['version_number'], version.version_number)

    def test_get_archive_version_detail_not_found(self):
        response = self.client.get(self.version_detail_url(self.archive1.id, 99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_archive_versions_permission_entry_user_own(self):
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.versions_url(self.archive1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_archive_versions_permission_entry_user_other(self):
        other_archive = Archive.objects.create(
            title='其他用户的案卷',
            description='描述',
            archive_number='ARCH-OTHER-001',
            category=self.category_child,
            status='draft',
            created_by=self.admin_user
        )
        self.client.force_authenticate(user=self.entry_user)
        response = self.client.get(self.versions_url(other_archive.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rollback_version(self):
        archive = self.archive1
        ArchiveVersion.create_snapshot(archive, self.admin_user, '初始状态')
        archive.title = '修改后的标题'
        archive.description = '修改后的描述'
        archive.status = 'approved'
        archive.save()
        ArchiveVersion.create_snapshot(archive, self.admin_user, '修改案卷')

        first_version = ArchiveVersion.objects.get(archive=archive, version_number=1)
        data = {'version_id': first_version.id}
        response = self.client.post(self.rollback_url(archive.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        archive.refresh_from_db()
        self.assertEqual(archive.title, '测试案卷1')
        self.assertEqual(archive.description, '这是第一个测试案卷')
        self.assertEqual(archive.status, 'draft')

    def test_rollback_version_permission_denied(self):
        self.client.force_authenticate(user=self.entry_user)
        version = ArchiveVersion.objects.filter(archive=self.archive1).first()
        data = {'version_id': version.id}
        response = self.client.post(self.rollback_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rollback_version_not_found(self):
        data = {'version_id': 99999}
        response = self.client.post(self.rollback_url(self.archive1.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rollback_version_invalid_data(self):
        response = self.client.post(self.rollback_url(self.archive1.id), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_creates_reject_record(self):
        archive = self.archive2
        reject_count_before = RejectRecord.objects.filter(archive=archive).count()
        version_count_before = ArchiveVersion.objects.filter(archive=archive).count()

        self.client.force_authenticate(user=self.review_user)
        data = {'comment': '需要补充更多信息'}
        response = self.client.post(self.reject_url(archive.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            RejectRecord.objects.filter(archive=archive).count(),
            reject_count_before + 1
        )
        self.assertEqual(
            ArchiveVersion.objects.filter(archive=archive).count(),
            version_count_before + 1
        )

        reject_record = RejectRecord.objects.filter(archive=archive).order_by('-rejected_at').first()
        self.assertEqual(reject_record.reject_comment, '需要补充更多信息')
        self.assertEqual(reject_record.rejected_by, self.review_user)
        self.assertIn('status', reject_record.field_changes)

    def test_get_reject_records(self):
        old_data = {'status': 'pending'}
        new_data = {'status': 'rejected'}
        RejectRecord.create_reject_record(
            self.archive2, self.review_user, '测试驳回', old_data, new_data
        )
        response = self.client.get(self.reject_records_url(self.archive2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_submit_for_review_marks_reject_resubmitted(self):
        archive = self.archive2
        self.client.force_authenticate(user=self.review_user)
        data = {'comment': '需要补充信息'}
        self.client.post(self.reject_url(archive.id), data, format='json')

        reject_record = RejectRecord.objects.filter(archive=archive, is_resubmitted=False).first()
        self.assertIsNotNone(reject_record)

        self.client.force_authenticate(user=self.entry_user)
        self.client.post(self.submit_url(archive.id))

        reject_record.refresh_from_db()
        self.assertTrue(reject_record.is_resubmitted)
        self.assertIsNotNone(reject_record.resubmitted_at)

    def test_reject_missing_comment(self):
        self.client.force_authenticate(user=self.review_user)
        response = self.client.post(self.reject_url(self.archive2.id), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
