from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ArchiveViewSet, TodoViewSet, login_view, logout_view, user_info_view

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'archives', ArchiveViewSet)
router.register(r'todos', TodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', user_info_view, name='user-info'),
]
