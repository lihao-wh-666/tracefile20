from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ArchiveDataMixin:
    ARCHIVE_DATA_FIELDS = [
        'title',
        'description',
        'archive_number',
        'category_id',
        'status',
    ]

    def to_dict(self, fields=None):
        fields = fields or self.ARCHIVE_DATA_FIELDS
        result = {}
        for field in fields:
            value = getattr(self, field, None)
            if isinstance(value, models.Model):
                value = value.id
            result[field] = value
        return result

    @classmethod
    def get_field_changes(cls, old_data, new_data):
        field_changes = {}
        for key in set(old_data.keys()) | set(new_data.keys()):
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            if old_val != new_val:
                field_changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        return field_changes
