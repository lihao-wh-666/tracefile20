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

    title = models.CharField(max_length=200, verbose_name='待办标题')
    description = models.TextField(blank=True, verbose_name='待办描述')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
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
    created_by = models.CharField(max_length=100, blank=True, verbose_name='创建人')

    class Meta:
        verbose_name = '案卷'
        verbose_name_plural = '案卷'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.archive_number} - {self.title}"
