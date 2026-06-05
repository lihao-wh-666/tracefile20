from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ArchiveViewSet, TodoViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'archives', ArchiveViewSet)
router.register(r'todos', TodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
