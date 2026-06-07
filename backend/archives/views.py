from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Archive, Todo, LoginAttempt, UserProfile, UserPreference
from .serializers import (
    CategorySerializer, CategorySimpleSerializer, ArchiveSerializer, TodoSerializer,
    UserInfoSerializer, UserUpdateSerializer, PasswordChangeSerializer,
    UserProfileSerializer, UserPreferenceSerializer
)
from django.utils.decorators import method_decorator


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
    filterset_fields = ['priority', 'status', 'is_read']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Todo.objects.filter(is_read=False, status='pending').count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Todo.objects.filter(is_read=False).update(is_read=True)
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

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.username if self.request.user.is_authenticated else 'system')
