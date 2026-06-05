from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Archive
from .serializers import CategorySerializer, CategorySimpleSerializer, ArchiveSerializer


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
