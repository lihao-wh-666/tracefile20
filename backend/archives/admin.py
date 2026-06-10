from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Category, Archive, Todo, LoginAttempt, UserProfile, UserPreference, ArchiveLog, ArchiveVersion, RejectRecord


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = '用户偏好'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserPreferenceInline)
    list_display = ['username', 'email', 'is_staff', 'is_active', 'get_groups']
    list_filter = ['is_staff', 'is_active', 'groups']

    def get_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    get_groups.short_description = '用户组'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ['archive_number', 'title', 'category', 'status', 'created_by', 'reviewed_by', 'created_at']
    search_fields = ['title', 'archive_number', 'description']
    list_filter = ['status', 'category', 'created_at', 'reviewed_at']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'reviewed_at']
    fieldsets = [
        ('基本信息', {'fields': ['archive_number', 'title', 'description', 'category']}),
        ('状态信息', {'fields': ['status', 'created_by', 'submitted_at']}),
        ('审核信息', {'fields': ['reviewed_by', 'reviewed_at', 'review_comment']}),
        ('时间信息', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'todo_type', 'priority', 'status', 'is_read', 'user', 'archive', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['priority', 'status', 'is_read', 'todo_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'failed_attempts', 'last_attempt_time', 'lock_until']
    search_fields = ['username']
    list_filter = ['lock_until']
    readonly_fields = ['last_attempt_time']


@admin.register(ArchiveLog)
class ArchiveLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'archive_number', 'archive_title', 'operator', 'ip_address', 'created_at']
    search_fields = ['archive_number', 'archive_title', 'operator', 'ip_address']
    list_filter = ['action_type', 'created_at']
    readonly_fields = ['created_at']
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ArchiveVersion)
class ArchiveVersionAdmin(admin.ModelAdmin):
    list_display = ['archive_number', 'version_number', 'title', 'category_name', 'status', 'created_by', 'created_at']
    search_fields = ['title', 'archive_number', 'description', 'category_name', 'change_reason']
    list_filter = ['status', 'version_number', 'created_at']
    readonly_fields = ['created_at', 'snapshot_data', 'archive', 'version_number', 'title', 'description', 'archive_number', 'category_id', 'category_name', 'status', 'created_by', 'change_reason']
    fieldsets = [
        ('版本信息', {'fields': ['archive', 'version_number', 'change_reason']}),
        ('案卷信息', {'fields': ['title', 'description', 'archive_number', 'category_id', 'category_name', 'status']}),
        ('快照数据', {'fields': ['snapshot_data']}),
        ('操作信息', {'fields': ['created_by', 'created_at']}),
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RejectRecord)
class RejectRecordAdmin(admin.ModelAdmin):
    list_display = ['archive', 'version_number', 'rejected_by', 'rejected_at', 'is_resubmitted', 'resubmitted_at']
    search_fields = ['reject_comment', 'archive__archive_number', 'archive__title']
    list_filter = ['is_resubmitted', 'rejected_at', 'resubmitted_at']
    readonly_fields = ['rejected_at', 'archive', 'reject_version', 'reject_comment', 'rejected_by', 'data_before', 'data_after', 'field_changes', 'is_resubmitted', 'resubmitted_at']
    fieldsets = [
        ('基本信息', {'fields': ['archive', 'reject_version']}),
        ('驳回信息', {'fields': ['reject_comment', 'rejected_by', 'rejected_at']}),
        ('数据变更', {'fields': ['data_before', 'data_after', 'field_changes']}),
        ('重新提交', {'fields': ['is_resubmitted', 'resubmitted_at']}),
    ]

    def version_number(self, obj):
        return obj.reject_version.version_number if obj.reject_version else '-'
    version_number.short_description = '驳回版本'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
