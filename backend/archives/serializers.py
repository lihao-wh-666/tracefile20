from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Archive, Todo, UserProfile, UserPreference, ArchiveLog, ArchiveVersion, RejectRecord
from django.contrib.auth.password_validation import validate_password
from .permissions import ARCHIVE_ENTRY_GROUP_NAME, ARCHIVE_REVIEW_GROUP_NAME


class UsernameSerializerMixin:
    def get_username(self, obj, user_field):
        user = getattr(obj, user_field, None)
        return user.username if user else None

    def get_created_by_username(self, obj):
        return self.get_username(obj, 'created_by')

    def get_reviewed_by_username(self, obj):
        return self.get_username(obj, 'reviewed_by')

    def get_rejected_by_username(self, obj):
        return self.get_username(obj, 'rejected_by')


class UserProfileSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'phone', 'gender', 'gender_display', 'avatar',
            'bio', 'department', 'position', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserPreferenceSerializer(serializers.ModelSerializer):
    theme_display = serializers.CharField(source='get_theme_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)

    class Meta:
        model = UserPreference
        fields = [
            'id', 'theme', 'theme_display', 'language', 'language_display',
            'email_notification', 'sound_effect', 'auto_save',
            'page_size', 'sidebar_collapsed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserInfoSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    preferences = UserPreferenceSerializer(read_only=True)
    groups = serializers.SerializerMethodField()
    is_archive_entry = serializers.SerializerMethodField()
    is_archive_review = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'profile', 'preferences',
            'groups', 'is_archive_entry', 'is_archive_review'
        ]
        read_only_fields = ['username', 'is_staff', 'is_active', 'date_joined']

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_is_archive_entry(self, obj):
        return obj.groups.filter(name=ARCHIVE_ENTRY_GROUP_NAME).exists()

    def get_is_archive_review(self, obj):
        return obj.groups.filter(name=ARCHIVE_REVIEW_GROUP_NAME).exists()


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)

        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码不正确')
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次输入的新密码不一致'})
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({'new_password': '新密码不能与旧密码相同'})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TodoSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    todo_type_display = serializers.CharField(source='get_todo_type_display', read_only=True)
    archive_title = serializers.CharField(source='archive.title', read_only=True)
    archive_number = serializers.CharField(source='archive.archive_number', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'status', 'status_display', 'todo_type', 'todo_type_display',
            'due_date', 'is_read', 'user', 'username', 'archive',
            'archive_title', 'archive_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'parent_name', 'children', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ArchiveSerializer(serializers.ModelSerializer, UsernameSerializerMixin):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.SerializerMethodField()
    reviewed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Archive
        fields = [
            'id', 'title', 'description', 'archive_number',
            'category', 'category_name', 'status', 'status_display',
            'created_at', 'updated_at', 'created_by', 'created_by_username',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'review_comment',
            'submitted_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'reviewed_by', 'reviewed_at', 'submitted_at']


class ArchiveLogSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = ArchiveLog
        fields = [
            'id', 'archive', 'archive_number', 'archive_title',
            'action_type', 'action_type_display', 'operator',
            'ip_address', 'change_content', 'created_at'
        ]
        read_only_fields = [
            'id', 'archive', 'archive_number', 'archive_title',
            'action_type', 'action_type_display', 'operator',
            'ip_address', 'change_content', 'created_at'
        ]


class ArchiveVersionSerializer(serializers.ModelSerializer, UsernameSerializerMixin):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = ArchiveVersion
        fields = [
            'id', 'archive', 'version_number', 'title', 'description',
            'archive_number', 'category_id', 'category_name',
            'status', 'status_display', 'snapshot_data',
            'created_by', 'created_by_username', 'change_reason', 'created_at'
        ]
        read_only_fields = [
            'id', 'archive', 'version_number', 'title', 'description',
            'archive_number', 'category_id', 'category_name',
            'status', 'status_display', 'snapshot_data',
            'created_by', 'created_by_username', 'change_reason', 'created_at'
        ]


class RejectRecordSerializer(serializers.ModelSerializer, UsernameSerializerMixin):
    rejected_by_username = serializers.SerializerMethodField()
    version_number = serializers.IntegerField(source='reject_version.version_number', read_only=True)

    class Meta:
        model = RejectRecord
        fields = [
            'id', 'archive', 'reject_version', 'version_number',
            'reject_comment', 'rejected_by', 'rejected_by_username',
            'rejected_at', 'data_before', 'data_after', 'field_changes',
            'is_resubmitted', 'resubmitted_at'
        ]
        read_only_fields = [
            'id', 'archive', 'reject_version', 'version_number',
            'reject_comment', 'rejected_by', 'rejected_by_username',
            'rejected_at', 'data_before', 'data_after', 'field_changes',
            'is_resubmitted', 'resubmitted_at'
        ]


class ArchiveRejectSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True, write_only=True)


class ArchiveRollbackSerializer(serializers.Serializer):
    version_id = serializers.IntegerField(required=True, write_only=True)
