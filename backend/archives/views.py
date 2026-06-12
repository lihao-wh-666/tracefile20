from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Archive, Todo, LoginAttempt, UserProfile, UserPreference, ArchiveLog, ArchiveVersion, RejectRecord
from .serializers import (
    CategorySerializer, CategorySimpleSerializer, ArchiveSerializer, TodoSerializer,
    UserInfoSerializer, UserUpdateSerializer, PasswordChangeSerializer,
    UserProfileSerializer, UserPreferenceSerializer, ArchiveLogSerializer,
    ArchiveVersionSerializer, RejectRecordSerializer, ArchiveRejectSerializer,
    ArchiveRollbackSerializer
)
from .permissions import (
    is_archive_entry_user, is_archive_review_user,
    ARCHIVE_REVIEW_GROUP_NAME, setup_archive_groups
)
from .pagination import StandardResultsSetPagination
from .export_service import export_archives
from .mixins.view_mixins import (
    ArchivePermissionMixin, ArchiveOperationMixin,
    get_client_ip, create_archive_log, create_review_todos_for_archive,
    create_notification_for_creator
)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'detail': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )

    is_locked, lock_until = LoginAttempt.is_locked(username)
    if is_locked:
        remaining_minutes = int((lock_until - timezone.now()).total_seconds() / 60) + 1
        return Response(
            {
                'detail': f'登录失败次数过多，账号已被锁定，请在 {remaining_minutes} 分钟后再试',
                'lock_until': lock_until
            },
            status=status.HTTP_403_FORBIDDEN
        )

    user = authenticate(request, username=username, password=password)

    if user is not None:
        LoginAttempt.reset_attempts(username)
        login(request, user)
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff
        })

    attempt = LoginAttempt.record_failed_attempt(username)
    remaining_attempts = LoginAttempt.MAX_ATTEMPTS - attempt.failed_attempts

    if remaining_attempts > 0:
        return Response(
            {
                'detail': f'用户名或密码错误，还有 {remaining_attempts} 次尝试机会',
                'remaining_attempts': remaining_attempts
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {
            'detail': f'登录失败次数过多，账号已被锁定 {LoginAttempt.LOCK_DURATION_MINUTES} 分钟',
            'lock_until': attempt.lock_until
        },
        status=status.HTTP_403_FORBIDDEN
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'detail': '已成功登出'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user
    UserProfile.objects.get_or_create(user=user)
    UserPreference.objects.get_or_create(user=user)
    return Response(UserInfoSerializer(user).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        UserProfile.objects.get_or_create(user=user)
        UserPreference.objects.get_or_create(user=user)
        return Response(UserInfoSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        update_session_auth_hash(request, user)
        return Response({'detail': '密码修改成功'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_preferences_view(request):
    user = request.user
    preferences, created = UserPreference.objects.get_or_create(user=user)

    if request.method == 'GET':
        return Response(UserPreferenceSerializer(preferences).data)

    serializer = UserPreferenceSerializer(preferences, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'status', 'is_read', 'todo_type']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset if user.is_staff else queryset.filter(user=user)

    def _get_user_queryset(self):
        queryset = Todo.objects.filter(is_read=False, status='pending')
        user = self.request.user
        return queryset if user.is_staff else queryset.filter(user=user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': self._get_user_queryset().count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self._get_user_queryset().update(is_read=True)
        return Response({'message': '已全部标记为已读'})

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        todo = self.get_object()
        todo.toggle_status()
        return Response(TodoSerializer(todo).data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    pagination_class = StandardResultsSetPagination
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        root_categories = Category.objects.filter(parent=None)
        return Response(CategorySerializer(root_categories, many=True).data)

    @action(detail=False, methods=['get'])
    def simple(self, request):
        return Response(CategorySimpleSerializer(Category.objects.all(), many=True).data)


class ArchiveViewSet(viewsets.ModelViewSet, ArchivePermissionMixin, ArchiveOperationMixin):
    queryset = Archive.objects.all()
    serializer_class = ArchiveSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description', 'archive_number']
    ordering_fields = ['created_at', 'updated_at', 'archive_number']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_archive_review_user(user):
            return queryset
        if is_archive_entry_user(user):
            return queryset.filter(created_by=user)
        return queryset.none()

    def _check_edit_permission(self, instance, user):
        if is_archive_entry_user(user) and instance.status in ['approved', 'pending']:
            raise PermissionDenied('案卷已提交审核或已通过，无法编辑')

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(
            created_by=user if user.is_authenticated else None,
            status='draft'
        )
        self.create_snapshot_and_log(self.request, instance, 'create', '创建案卷')

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        self._check_edit_permission(instance, user)
        old_data = self.get_old_data(instance)

        if is_archive_entry_user(user) and 'status' in serializer.validated_data:
            serializer.validated_data.pop('status', None)

        change_reason = self.request.data.get('change_reason', '更新案卷')
        instance = serializer.save()

        self.create_snapshot_and_log(self.request, instance, 'update', change_reason, old_data=old_data)

    def perform_destroy(self, instance):
        user = self.request.user
        if is_archive_entry_user(user):
            raise PermissionDenied('您没有删除案卷的权限')

        old_data = self.get_old_data(instance)
        create_archive_log(self.request, instance, 'delete', old_data=old_data)
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        create_archive_log(request, instance, 'view')
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_for_review(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        self.check_archive_permission(archive, user, 'submit')
        self.check_archive_status(archive, ['draft', 'rejected'], '当前状态无法提交审核')

        old_data = self.get_old_data(archive)
        archive.transition_status(
            'submit',
            submitted_at=timezone.now(),
            reviewed_by=None,
            reviewed_at=None,
            review_comment=''
        )

        self.create_snapshot_and_log(request, archive, 'update', '提交审核', old_data=old_data)
        self.mark_resubmitted_records(archive)
        create_review_todos_for_archive(archive, ARCHIVE_REVIEW_GROUP_NAME, user.username)

        return Response(ArchiveSerializer(archive).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        self.check_archive_permission(archive, user, 'review')
        self.check_archive_status(archive, ['pending'], '只有待审核状态的案卷才能通过')

        comment = request.data.get('comment', '')
        old_data = self.get_old_data(archive)

        archive.transition_status(
            'approve',
            reviewed_by=user,
            reviewed_at=timezone.now(),
            review_comment=comment
        )

        change_reason = f'审核通过：{comment}' if comment else '审核通过'
        self.create_snapshot_and_log(request, archive, 'update', change_reason, old_data=old_data)
        create_notification_for_creator(archive, 'approved', comment)

        return Response(ArchiveSerializer(archive).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        self.check_archive_permission(archive, user, 'review')
        self.check_archive_status(archive, ['pending'], '只有待审核状态的案卷才能驳回')

        serializer = ArchiveRejectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.validated_data['comment']
        old_data = self.get_old_data(archive)

        archive.transition_status(
            'reject',
            reviewed_by=user,
            reviewed_at=timezone.now(),
            review_comment=comment
        )

        self.create_snapshot_and_log(request, archive, 'update', f'审核驳回：{comment}', old_data=old_data)
        self.handle_reject_record(archive, user, comment, old_data, self.get_old_data(archive))
        create_notification_for_creator(archive, 'rejected', comment)

        return Response(ArchiveSerializer(archive).data)

    def _check_version_permission(self, request, archive):
        user = request.user
        if not user.is_staff and not is_archive_review_user(user):
            if is_archive_entry_user(user) and archive.created_by != user:
                raise PermissionDenied('您没有权限查看该案卷的版本记录')

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def versions(self, request, pk=None):
        archive = self.get_object()
        self._check_version_permission(request, archive)
        return Response(ArchiveVersionSerializer(archive.versions.all(), many=True).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='versions/(?P<version_id>[^/.]+)')
    def version_detail(self, request, pk=None, version_id=None):
        archive = self.get_object()
        self._check_version_permission(request, archive)

        try:
            version = ArchiveVersion.objects.get(archive=archive, id=version_id)
        except ArchiveVersion.DoesNotExist:
            return Response(
                {'detail': '版本不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ArchiveVersionSerializer(version).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rollback(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        self.check_archive_permission(archive, user, 'rollback')

        serializer = ArchiveRollbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            version = ArchiveVersion.objects.get(archive=archive, id=serializer.validated_data['version_id'])
        except ArchiveVersion.DoesNotExist:
            return Response(
                {'detail': '版本不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        restored_archive, old_data, new_data = version.restore(user)
        create_archive_log(request, restored_archive, 'update', old_data=old_data, new_data=new_data)

        return Response(ArchiveSerializer(restored_archive).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def reject_records(self, request, pk=None):
        archive = self.get_object()
        self._check_version_permission(request, archive)
        return Response(RejectRecordSerializer(archive.reject_records.all(), many=True).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def export(self, request):
        archive_ids = request.data.get('ids', [])
        export_format = request.data.get('format', 'xlsx')

        if not archive_ids:
            return Response(
                {'detail': '请选择要导出的案卷'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(archive_ids, str):
            archive_ids = [aid.strip() for aid in archive_ids.split(',') if aid.strip()]

        valid_formats = ['pdf', 'xlsx', 'excel', 'word', 'docx', 'csv']
        if export_format.lower() not in valid_formats:
            return Response(
                {'detail': f'不支持的导出格式：{export_format}，支持的格式：{", ".join(valid_formats)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset()
        archives = queryset.filter(id__in=archive_ids).order_by('-created_at')

        if not archives.exists():
            return Response(
                {'detail': '未找到可导出的案卷'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            return export_archives(archives, export_format)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': f'导出失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArchiveLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchiveLog.objects.all()
    serializer_class = ArchiveLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action_type', 'operator', 'archive_number']
    search_fields = ['archive_number', 'archive_title', 'operator', 'ip_address']
    ordering_fields = ['created_at', 'action_type', 'operator']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']


class ArchiveVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchiveVersion.objects.all()
    serializer_class = ArchiveVersionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archive', 'version_number', 'status', 'created_by']
    search_fields = ['title', 'description', 'archive_number', 'category_name', 'change_reason']
    ordering_fields = ['created_at', 'version_number']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_archive_review_user(user):
            return queryset
        if is_archive_entry_user(user):
            return queryset.filter(archive__created_by=user)
        return queryset.none()


class RejectRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RejectRecord.objects.all()
    serializer_class = RejectRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archive', 'rejected_by', 'is_resubmitted']
    search_fields = ['reject_comment', 'archive__archive_number', 'archive__title']
    ordering_fields = ['rejected_at', 'resubmitted_at']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    ordering = ['-rejected_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff or is_archive_review_user(user):
            return queryset
        if is_archive_entry_user(user):
            return queryset.filter(archive__created_by=user)
        return queryset.none()
