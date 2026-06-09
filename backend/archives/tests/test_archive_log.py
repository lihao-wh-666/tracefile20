from django.test import TestCase
from django.utils import timezone
from archives.models import ArchiveLog, Archive
from .base import BaseTestSetup


class ArchiveLogModelTests(BaseTestSetup):
    def test_archive_log_creation(self):
        log = ArchiveLog.objects.create(
            archive=self.archive1,
            archive_number=self.archive1.archive_number,
            archive_title=self.archive1.title,
            action_type='create',
            operator='testuser',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log.archive, self.archive1)
        self.assertEqual(log.archive_number, 'ARCH-001')
        self.assertEqual(log.archive_title, '测试案卷1')
        self.assertEqual(log.action_type, 'create')
        self.assertEqual(log.operator, 'testuser')
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertIsNone(log.change_content)
        self.assertIsNotNone(log.created_at)

    def test_archive_log_with_change_content(self):
        log = ArchiveLog.objects.create(
            archive=self.archive1,
            archive_number=self.archive1.archive_number,
            archive_title=self.archive1.title,
            action_type='update',
            operator='admin',
            ip_address='127.0.0.1',
            change_content={'old': {'title': '旧标题'}, 'new': {'title': '新标题'}}
        )
        self.assertEqual(log.change_content['old']['title'], '旧标题')
        self.assertEqual(log.change_content['new']['title'], '新标题')

    def test_archive_log_null_archive(self):
        log = ArchiveLog.objects.create(
            archive=None,
            archive_number='ARCH-DELETED',
            archive_title='已删除的案卷',
            action_type='delete',
            operator='admin',
            ip_address='10.0.0.1'
        )
        self.assertIsNone(log.archive)
        self.assertEqual(log.archive_number, 'ARCH-DELETED')

    def test_archive_log_action_choices(self):
        for action_val, _ in ArchiveLog.ACTION_CHOICES:
            log = ArchiveLog(
                archive_number=f'ARCH-{action_val}',
                action_type=action_val,
                operator='test',
                ip_address='127.0.0.1'
            )
            log.full_clean()
            log.save()
            self.assertEqual(log.action_type, action_val)

    def test_archive_log_str_method(self):
        log = ArchiveLog.objects.create(
            archive=self.archive1,
            archive_number=self.archive1.archive_number,
            archive_title=self.archive1.title,
            action_type='create',
            operator='admin',
            ip_address='127.0.0.1'
        )
        expected = '创建 - ARCH-001 - admin'
        self.assertEqual(str(log), expected)

    def test_archive_log_ordering(self):
        log1 = ArchiveLog.objects.create(
            archive_number='LOG-1', action_type='create',
            operator='user1', ip_address='127.0.0.1'
        )
        log2 = ArchiveLog.objects.create(
            archive_number='LOG-2', action_type='update',
            operator='user2', ip_address='127.0.0.1'
        )
        logs = list(ArchiveLog.objects.all())
        self.assertEqual(logs[0].pk, log2.pk)

    def test_archive_log_blank_archive_title(self):
        log = ArchiveLog.objects.create(
            archive_number='ARCH-BLANK-TITLE',
            action_type='delete',
            operator='admin',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.archive_title, '')

    def test_archive_log_delete_set_null(self):
        log = ArchiveLog.objects.create(
            archive=self.archive1,
            archive_number=self.archive1.archive_number,
            archive_title=self.archive1.title,
            action_type='create',
            operator='admin',
            ip_address='127.0.0.1'
        )
        log_id = log.id
        archive_id = self.archive1.id
        Archive.objects.filter(id=archive_id).delete()
        log.refresh_from_db()
        self.assertTrue(ArchiveLog.objects.filter(id=log_id).exists())
        self.assertIsNone(log.archive)
