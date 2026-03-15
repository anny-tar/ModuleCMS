from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(ModelAdmin):
    list_display  = ['preview', 'original_name', 'media_type',
                     'file_size_display', 'uploaded_by', 'uploaded_at']
    list_filter   = ['media_type', 'uploaded_at']
    search_fields = ['original_name', 'alt_text']
    readonly_fields = ['preview', 'original_name', 'media_type',
                       'file_size', 'uploaded_by', 'uploaded_at']

    def save_model(self, request, obj, form, change):
        # Автоматическая привязка пользователя при загрузке
        if not obj.pk:
            obj.uploaded_by = request.user
        if obj.file and not obj.original_name:
            obj.original_name = obj.file.name.split('/')[-1]
        super().save_model(request, obj, form, change)

    @admin.display(description='Превью')
    def preview(self, obj):
        if obj.is_image and obj.file:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;">',
                obj.url
            )
        return obj.get_media_type_display()

    @admin.display(description='Размер')
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f'{obj.file_size} Б'
        elif obj.file_size < 1024 * 1024:
            return f'{obj.file_size // 1024} КБ'
        return f'{obj.file_size // (1024 * 1024)} МБ'