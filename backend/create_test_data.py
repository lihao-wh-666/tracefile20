import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive_system.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.utils import timezone
from archives.models import Category, Archive, ArchiveVersion, RejectRecord


def create_test_data():
    print('=== 开始创建测试数据 ===')

    entry_group, _ = Group.objects.get_or_create(name='档案录入员')
    review_group, _ = Group.objects.get_or_create(name='档案审核员')

    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()
    admin_user.groups.add(entry_group, review_group)

    entry_user, _ = User.objects.get_or_create(
        username='entry_test',
        defaults={
            'email': 'entry@test.com',
            'is_staff': False
        }
    )
    entry_user.set_password('test123456')
    entry_user.save()
    entry_user.groups.add(entry_group)

    review_user, _ = User.objects.get_or_create(
        username='review_test',
        defaults={
            'email': 'review@test.com',
            'is_staff': False
        }
    )
    review_user.set_password('test123456')
    review_user.save()
    review_user.groups.add(review_group)

    admin_test_user, _ = User.objects.get_or_create(
        username='admin_test',
        defaults={
            'email': 'admin_test@test.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_test_user.set_password('test123456')
    admin_test_user.save()

    print('✓ 测试用户创建完成:')
    print(f'  - 管理员: admin / admin123 (默认账号)')
    print(f'  - 录入员: entry_test / test123456')
    print(f'  - 审核员: review_test / test123456')
    print(f'  - 管理员(测试): admin_test / test123456')

    cat1, _ = Category.objects.get_or_create(
        name='人事档案',
        defaults={'description': '人事相关档案'}
    )
    cat2, _ = Category.objects.get_or_create(
        name='合同档案',
        defaults={'description': '合同相关档案', 'parent': cat1}
    )
    cat3, _ = Category.objects.get_or_create(
        name='财务档案',
        defaults={'description': '财务相关档案', 'parent': cat1}
    )

    print('✓ 测试分类创建完成')

    archives_data = [
        {
            'title': '张三入职档案',
            'description': '张三2024年入职材料，包括简历、学历证明、劳动合同等',
            'archive_number': 'RS-2024-001',
            'category': cat2
        },
        {
            'title': '李四劳动合同',
            'description': '李四2023年续签的劳动合同，期限3年',
            'archive_number': 'HT-2023-015',
            'category': cat2
        },
        {
            'title': '2024年Q1财务报表',
            'description': '2024年第一季度财务报表，包括资产负债表、利润表、现金流量表',
            'archive_number': 'CW-2024-Q1',
            'category': cat3
        },
        {
            'title': '王五离职档案',
            'description': '王五2024年离职材料，包括离职申请、交接清单、离职证明',
            'archive_number': 'RS-2024-056',
            'category': cat2
        },
        {
            'title': '采购合同-2024-001',
            'description': '2024年度办公设备采购合同，金额50万元',
            'archive_number': 'CG-2024-001',
            'category': cat2
        }
    ]

    for data in archives_data:
        archive, created = Archive.objects.get_or_create(
            archive_number=data['archive_number'],
            defaults={
                'title': data['title'],
                'description': data['description'],
                'category': data['category'],
                'status': 'draft',
                'created_by': entry_user
            }
        )
        if created:
            ArchiveVersion.create_snapshot(archive, entry_user, '创建案卷')
            print(f'✓ 创建案卷: {data["archive_number"]} - {data["title"]}')

            archive.title = data['title'] + '（已完善）'
            archive.description = data['description'] + '\n\n补充：材料已审核完整。'
            archive.save()
            ArchiveVersion.create_snapshot(archive, entry_user, '完善档案信息')

            archive.status = 'pending'
            archive.submitted_at = timezone.now()
            archive.save()
            ArchiveVersion.create_snapshot(archive, entry_user, '提交审核')

            if data['archive_number'] in ['HT-2023-015', 'CW-2024-Q1']:
                old_data = {
                    'title': archive.title,
                    'description': archive.description,
                    'status': 'pending'
                }
                archive.status = 'rejected'
                archive.reviewed_by = review_user
                archive.reviewed_at = timezone.now()
                archive.review_comment = '请补充完整的扫描件和审批流程记录。'
                archive.save()
                new_data = {
                    'title': archive.title,
                    'description': archive.description,
                    'status': 'rejected'
                }
                ArchiveVersion.create_snapshot(archive, review_user, '审核驳回：请补充完整的扫描件和审批流程记录。')
                RejectRecord.create_reject_record(archive, review_user, '请补充完整的扫描件和审批流程记录。', old_data, new_data)
                print(f'  → 已驳回: {data["archive_number"]}')
            else:
                archive.status = 'approved'
                archive.reviewed_by = review_user
                archive.reviewed_at = timezone.now()
                archive.review_comment = '材料完整，审核通过。'
                archive.save()
                ArchiveVersion.create_snapshot(archive, review_user, '审核通过：材料完整，审核通过。')
                print(f'  → 已通过: {data["archive_number"]}')

    print('\n=== 测试数据创建完成 ===')
    print('\n=== 测试场景说明 ===')
    print('1. 版本快照测试: 每个案卷都有3个版本（创建→完善→提交/审核）')
    print('2. 驳回记录测试: HT-2023-015 和 CW-2024-Q1 有驳回记录')
    print('3. 版本回滚测试: 可以将已通过的案卷回滚到历史版本')
    print('\n登录账号:')
    print('  录入员: entry_test / test123456')
    print('  审核员: review_test / test123456')
    print('  管理员: admin_test / test123456')


if __name__ == '__main__':
    create_test_data()
