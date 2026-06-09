from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import Group
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Archive, Todo, LoginAttempt, UserProfile, UserPreference, ArchiveLog
from .serializers import (
    CategorySerializer, CategorySimpleSerializer, ArchiveSerializer, TodoSerializer,
    UserInfoSerializer, UserUpdateSerializer, PasswordChangeSerializer,
    UserProfileSerializer, UserPreferenceSerializer, ArchiveLogSerializer
)
from .permissions import (
    is_archive_entry_user, is_archive_review_user,
    ARCHIVE_ENTRY_GROUP_NAME, ARCHIVE_REVIEW_GROUP_NAME,
    setup_archive_groups
)
from .pagination import StandardResultsSetPagination
from .export_service import export_archives
from django.utils.decorators import method_decorator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def create_archive_log(request, archive, action_type, old_data=None, new_data=None):
    operator = request.user.username if request.user.is_authenticated else 'anonymous'
    ip_address = get_client_ip(request)

    change_content = None
    if old_data is not None or new_data is not None:
        change_content = {
            'old': old_data,
            'new': new_data
        }

    ArchiveLog.objects.create(
        archive=archive,
        archive_number=archive.archive_number if archive else '',
        archive_title=archive.title if archive else '',
        action_type=action_type,
        operator=operator,
        ip_address=ip_address,
        change_content=change_content
    )


def create_review_todos_for_archive(archive, created_by_username=''):
    try:
        review_group = Group.objects.get(name=ARCHIVE_REVIEW_GROUP_NAME)
    except Group.DoesNotExist:
        return

    users = review_group.user_set.all()
    for user in users:
        Todo.objects.create(
            title=f'案卷待审核：{archive.archive_number}',
            description=f'案卷「{archive.title}」已提交审核，请及时处理。\n提交人：{created_by_username}',
            priority='high',
            status='pending',
            todo_type='review',
            is_read=False,
            user=user,
            archive=archive
        )


def create_notification_for_creator(archive, action, comment=''):
    if not archive.created_by:
        return

    action_text = {
        'approved': '审核通过',
        'rejected': '审核驳回',
    }.get(action, '审核完成')

    description = f'您的案卷「{archive.title}」已{action_text}。'
    if comment:
        description += f'\n审核意见：{comment}'

    Todo.objects.create(
        title=f'案卷{action_text}：{archive.archive_number}',
        description=description,
        priority='medium',
        status='pending',
        todo_type='notification',
        is_read=False,
        user=archive.created_by,
        archive=archive
    )


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    csrf_token = get_token(request)
    return Response({'csrfToken': csrf_token})


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
    else:
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
        else:
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
    serializer = UserInfoSerializer(user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        user = request.user
        UserProfile.objects.get_or_create(user=user)
        UserPreference.objects.get_or_create(user=user)
        result_serializer = UserInfoSerializer(user)
        return Response(result_serializer.data)
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
        serializer = UserPreferenceSerializer(preferences)
        return Response(serializer.data)

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
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

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
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        user = request.user
        queryset = Todo.objects.filter(is_read=False, status='pending')
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        count = queryset.count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        user = request.user
        queryset = Todo.objects.filter(is_read=False)
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        queryset.update(is_read=True)
        return Response({'message': '已全部标记为已读'})

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        todo = self.get_object()
        todo.status = 'completed' if todo.status == 'pending' else 'pending'
        todo.save()
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
        serializer = CategorySerializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def simple(self, request):
        categories = Category.objects.all()
        serializer = CategorySimpleSerializer(categories, many=True)
        return Response(serializer.data)


class ArchiveViewSet(viewsets.ModelViewSet):
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
        if user.is_staff:
            return queryset
        if is_archive_review_user(user):
            return queryset
        if is_archive_entry_user(user):
            return queryset.filter(created_by=user)
        return queryset.none()

    def get_old_data(self, instance):
        return {
            'title': instance.title,
            'description': instance.description,
            'archive_number': instance.archive_number,
            'category_id': instance.category_id,
            'status': instance.status
        }

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(
            created_by=user if user.is_authenticated else None,
            status='draft'
        )
        new_data = self.get_old_data(instance)
        create_archive_log(self.request, instance, 'create', new_data=new_data)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        if is_archive_entry_user(user) and instance.status in ['approved', 'pending']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('案卷已提交审核或已通过，无法编辑')

        old_data = self.get_old_data(instance)

        if is_archive_entry_user(user) and 'status' in serializer.validated_data:
            serializer.validated_data.pop('status', None)

        instance = serializer.save()
        new_data = self.get_old_data(instance)
        create_archive_log(self.request, instance, 'update', old_data=old_data, new_data=new_data)

    def perform_destroy(self, instance):
        user = self.request.user
        if is_archive_entry_user(user):
            from rest_framework.exceptions import PermissionDenied
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

        if not is_archive_entry_user(user) and not user.is_staff:
            return Response(
                {'detail': '您没有提交审核的权限'},
                status=status.HTTP_403_FORBIDDEN
            )

        if is_archive_entry_user(user) and archive.created_by != user:
            return Response(
                {'detail': '只能提交自己创建的案卷'},
                status=status.HTTP_403_FORBIDDEN
            )

        if archive.status not in ['draft', 'rejected']:
            return Response(
                {'detail': '当前状态无法提交审核'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_data = self.get_old_data(archive)
        archive.status = 'pending'
        archive.submitted_at = timezone.now()
        archive.reviewed_by = None
        archive.reviewed_at = None
        archive.review_comment = ''
        archive.save()

        new_data = self.get_old_data(archive)
        create_archive_log(request, archive, 'update', old_data=old_data, new_data=new_data)

        create_review_todos_for_archive(archive, user.username)

        return Response(ArchiveSerializer(archive).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        if not is_archive_review_user(user) and not user.is_staff:
            return Response(
                {'detail': '您没有审核权限'},
                status=status.HTTP_403_FORBIDDEN
            )

        if archive.status != 'pending':
            return Response(
                {'detail': '只有待审核状态的案卷才能通过'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = request.data.get('comment', '')

        old_data = self.get_old_data(archive)
        archive.status = 'approved'
        archive.reviewed_by = user
        archive.reviewed_at = timezone.now()
        archive.review_comment = comment
        archive.save()

        new_data = self.get_old_data(archive)
        create_archive_log(request, archive, 'update', old_data=old_data, new_data=new_data)

        create_notification_for_creator(archive, 'approved', comment)

        return Response(ArchiveSerializer(archive).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        archive = self.get_object()
        user = request.user

        if not is_archive_review_user(user) and not user.is_staff:
            return Response(
                {'detail': '您没有审核权限'},
                status=status.HTTP_403_FORBIDDEN
            )

        if archive.status != 'pending':
            return Response(
                {'detail': '只有待审核状态的案卷才能驳回'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = request.data.get('comment', '')
        if not comment:
            return Response(
                {'detail': '驳回时必须填写审核意见'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_data = self.get_old_data(archive)
        archive.status = 'rejected'
        archive.reviewed_by = user
        archive.reviewed_at = timezone.now()
        archive.review_comment = comment
        archive.save()

        new_data = self.get_old_data(archive)
        create_archive_log(request, archive, 'update', old_data=old_data, new_data=new_data)

        create_notification_for_creator(archive, 'rejected', comment)

        return Response(ArchiveSerializer(archive).data)

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
            response = export_archives(archives, export_format)
            return response
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
