from django.contrib import admin
from .models import Category, Archive


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ['archive_number', 'title', 'category', 'status', 'created_at', 'created_by']
    search_fields = ['title', 'archive_number', 'description']
    list_filter = ['status', 'category', 'created_at']
