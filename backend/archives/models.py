from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='性别')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    department = models.CharField(max_length=100, blank=True, verbose_name='部门')
    position = models.CharField(max_length=100, blank=True, verbose_name='职位')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return self.user.username


class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', '浅色主题'),
        ('dark', '深色主题'),
        ('auto', '跟随系统'),
    ]

    LANGUAGE_CHOICES = [
        ('zh-CN', '简体中文'),
        ('en', 'English'),
        ('ja', '日本語'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences', verbose_name='用户')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light', verbose_name='主题')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='zh-CN', verbose_name='语言')
    email_notification = models.BooleanField(default=True, verbose_name='邮件通知')
    sound_effect = models.BooleanField(default=False, verbose_name='音效')
    auto_save = models.BooleanField(default=True, verbose_name='自动保存')
    page_size = models.IntegerField(default=10, verbose_name='每页条数')
    sidebar_collapsed = models.BooleanField(default=False, verbose_name='侧边栏收起')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'

    def __str__(self):
        return f"{self.user.username}的偏好设置"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    failed_attempts = models.IntegerField(default=0, verbose_name='失败次数')
    last_attempt_time = models.DateTimeField(null=True, blank=True, verbose_name='最后尝试时间')
    lock_until = models.DateTimeField(null=True, blank=True, verbose_name='锁定截止时间')

    class Meta:
        verbose_name = '登录尝试记录'
        verbose_name_plural = '登录尝试记录'

    def __str__(self):
        return self.username

    MAX_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 60

    @classmethod
    def is_locked(cls, username):
        try:
            attempt = cls.objects.get(username=username)
            if attempt.lock_until and attempt.lock_until > timezone.now():
                return True, attempt.lock_until
            return False, None
        except cls.DoesNotExist:
            return False, None

    @classmethod
    def record_failed_attempt(cls, username):
        attempt, created = cls.objects.get_or_create(username=username)
        attempt.failed_attempts += 1
        attempt.last_attempt_time = timezone.now()
        if attempt.failed_attempts >= cls.MAX_ATTEMPTS:
            attempt.lock_until = timezone.now() + timezone.timedelta(minutes=cls.LOCK_DURATION_MINUTES)
        attempt.save()
        return attempt

    @classmethod
    def reset_attempts(cls, username):
        try:
            attempt = cls.objects.get(username=username)
            attempt.failed_attempts = 0
            attempt.lock_until = None
            attempt.save()
        except cls.DoesNotExist:
            pass


class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    ]

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('completed', '已完成'),
    ]

    TODO_TYPE_CHOICES = [
        ('general', '普通'),
        ('review', '审核'),
        ('notification', '通知'),
    ]

    title = models.CharField(max_length=200, verbose_name='待办标题')
    description = models.TextField(blank=True, verbose_name='待办描述')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    todo_type = models.CharField(max_length=20, choices=TODO_TYPE_CHOICES, default='general', verbose_name='待办类型')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='todos', verbose_name='所属用户')
    archive = models.ForeignKey('Archive', on_delete=models.CASCADE, null=True, blank=True, related_name='todos', verbose_name='关联案卷')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '待办事项'
        verbose_name_plural = '待办事项'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Archive(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    ]

    title = models.CharField(max_length=200, verbose_name='案卷标题')
    description = models.TextField(verbose_name='案卷描述')
    archive_number = models.CharField(max_length=100, unique=True, verbose_name='案卷编号')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='archives', verbose_name='所属分类')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_archives', verbose_name='创建人')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_archives', verbose_name='审核人')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')
    review_comment = models.TextField(blank=True, verbose_name='审核意见')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交审核时间')

    class Meta:
        verbose_name = '案卷'
        verbose_name_plural = '案卷'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.archive_number} - {self.title}"


class ArchiveLog(models.Model):
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '预览'),
    ]

    archive = models.ForeignKey(
        Archive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        verbose_name='关联案卷'
    )
    archive_number = models.CharField(max_length=100, verbose_name='案卷编号')
    archive_title = models.CharField(max_length=200, blank=True, verbose_name='案卷标题')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    operator = models.CharField(max_length=100, verbose_name='操作人')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    change_content = models.JSONField(null=True, blank=True, verbose_name='变更内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '案卷操作日志'
        verbose_name_plural = '案卷操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.archive_number} - {self.operator}"


class ArchiveVersion(models.Model):
    archive = models.ForeignKey(
        Archive,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='关联案卷'
    )
    version_number = models.IntegerField(verbose_name='版本号')
    title = models.CharField(max_length=200, verbose_name='案卷标题')
    description = models.TextField(verbose_name='案卷描述')
    archive_number = models.CharField(max_length=100, verbose_name='案卷编号')
    category_id = models.IntegerField(verbose_name='分类ID')
    category_name = models.CharField(max_length=100, verbose_name='分类名称')
    status = models.CharField(max_length=20, choices=Archive.STATUS_CHOICES, verbose_name='状态')
    snapshot_data = models.JSONField(verbose_name='快照数据')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_archive_versions',
        verbose_name='创建人'
    )
    change_reason = models.TextField(blank=True, verbose_name='修改原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '案卷版本快照'
        verbose_name_plural = '案卷版本快照'
        ordering = ['archive', '-version_number']
        unique_together = ['archive', 'version_number']

    def __str__(self):
        return f"{self.archive_number} - 版本{self.version_number}"

    @classmethod
    def create_snapshot(cls, archive, created_by, change_reason=''):
        last_version = cls.objects.filter(archive=archive).order_by('-version_number').first()
        version_number = last_version.version_number + 1 if last_version else 1

        snapshot_data = {
            'title': archive.title,
            'description': archive.description,
            'archive_number': archive.archive_number,
            'category_id': archive.category_id,
            'category_name': archive.category.name if archive.category else '',
            'status': archive.status,
            'created_by_id': archive.created_by_id,
            'reviewed_by_id': archive.reviewed_by_id,
            'reviewed_at': archive.reviewed_at.isoformat() if archive.reviewed_at else None,
            'review_comment': archive.review_comment,
            'submitted_at': archive.submitted_at.isoformat() if archive.submitted_at else None,
        }

        return cls.objects.create(
            archive=archive,
            version_number=version_number,
            title=archive.title,
            description=archive.description,
            archive_number=archive.archive_number,
            category_id=archive.category_id,
            category_name=archive.category.name if archive.category else '',
            status=archive.status,
            snapshot_data=snapshot_data,
            created_by=created_by,
            change_reason=change_reason
        )

    def restore(self, restored_by):
        from .models import Archive
        archive = self.archive

        old_data = {
            'title': archive.title,
            'description': archive.description,
            'archive_number': archive.archive_number,
            'category_id': archive.category_id,
            'status': archive.status
        }

        archive.title = self.title
        archive.description = self.description
        archive.archive_number = self.archive_number
        archive.status = 'draft'
        archive.reviewed_by = None
        archive.reviewed_at = None
        archive.review_comment = ''
        archive.submitted_at = None
        archive.save()

        new_data = {
            'title': archive.title,
            'description': archive.description,
            'archive_number': archive.archive_number,
            'category_id': archive.category_id,
            'status': archive.status
        }

        self.create_snapshot(archive, restored_by, f'回滚到版本{self.version_number}')

        return archive, old_data, new_data


class RejectRecord(models.Model):
    archive = models.ForeignKey(
        Archive,
        on_delete=models.CASCADE,
        related_name='reject_records',
        verbose_name='关联案卷'
    )
    reject_version = models.ForeignKey(
        ArchiveVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reject_records',
        verbose_name='驳回时版本'
    )
    reject_comment = models.TextField(verbose_name='驳回意见')
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_records',
        verbose_name='驳回人'
    )
    rejected_at = models.DateTimeField(auto_now_add=True, verbose_name='驳回时间')
    data_before = models.JSONField(verbose_name='修改前数据')
    data_after = models.JSONField(verbose_name='修改后数据')
    field_changes = models.JSONField(verbose_name='字段变更详情')
    is_resubmitted = models.BooleanField(default=False, verbose_name='是否已重新提交')
    resubmitted_at = models.DateTimeField(null=True, blank=True, verbose_name='重新提交时间')

    class Meta:
        verbose_name = '驳回记录'
        verbose_name_plural = '驳回记录'
        ordering = ['-rejected_at']

    def __str__(self):
        return f"{self.archive.archive_number} - 驳回记录"

    @classmethod
    def create_reject_record(cls, archive, rejected_by, reject_comment, old_data, new_data):
        field_changes = {}
        for key in set(old_data.keys()) | set(new_data.keys()):
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            if old_val != new_val:
                field_changes[key] = {
                    'old': old_val,
                    'new': new_val
                }

        current_version = ArchiveVersion.objects.filter(archive=archive).order_by('-version_number').first()

        return cls.objects.create(
            archive=archive,
            reject_version=current_version,
            reject_comment=reject_comment,
            rejected_by=rejected_by,
            data_before=old_data,
            data_after=new_data,
            field_changes=field_changes
        )

    def mark_resubmitted(self):
        from django.utils import timezone
        self.is_resubmitted = True
        self.resubmitted_at = timezone.now()
        self.save()
