from django.contrib import admin
from django.utils.html import format_html
from .models import LeadSubmission


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'section_id', 'data_preview',
                     'is_viewed', 'created_at']
    list_editable = ['is_viewed']
    list_filter   = ['is_viewed', 'created_at']
    readonly_fields = ['section_id', 'data', 'ip_address', 'created_at']

    @admin.display(description='Данные')
    def data_preview(self, obj):
        # Краткий просмотр данных заявки в списке
        items = [f'{k}: {v}' for k, v in obj.data.items()]
        return format_html('<br>'.join(items[:3]))