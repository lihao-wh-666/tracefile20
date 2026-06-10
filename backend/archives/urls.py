from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ArchiveViewSet, TodoViewSet, ArchiveLogViewSet,
    ArchiveVersionViewSet, RejectRecordViewSet,
    login_view, logout_view, user_info_view, csrf_token_view,
    update_user_info, change_password, user_preferences_view, user_profile_view
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'archives', ArchiveViewSet)
router.register(r'todos', TodoViewSet)
router.register(r'archive-logs', ArchiveLogViewSet)
router.register(r'archive-versions', ArchiveVersionViewSet)
router.register(r'reject-records', RejectRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', csrf_token_view, name='csrf-token'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', user_info_view, name='user-info'),
    path('auth/user/update/', update_user_info, name='user-update'),
    path('auth/password/change/', change_password, name='password-change'),
    path('user/profile/', user_profile_view, name='user-profile'),
    path('user/preferences/', user_preferences_view, name='user-preferences'),
]
