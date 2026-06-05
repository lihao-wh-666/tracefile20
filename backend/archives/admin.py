from django.contrib import admin
from .models import Category, Archive, Todo, LoginAttempt


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


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'is_read', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['priority', 'status', 'is_read', 'created_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'failed_attempts', 'last_attempt_time', 'lock_until']
    search_fields = ['username']
    list_filter = ['lock_until']
    readonly_fields = ['last_attempt_time']
