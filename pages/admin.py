from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from .models import Page, Section, PageType
from .forms import SectionAdminForm, SECTION_FORM_MAP

SECTION_BADGE_COLORS = {
    'hero':         '#6366f1',
    'text':         '#64748b',
    'counters':     '#0891b2',
    'cards':        '#0284c7',
    'team':         '#7c3aed',
    'steps':        '#059669',
    'table':        '#d97706',
    'chart_pie':    '#dc2626',
    'form':         '#db2777',
    'faq':          '#65a30d',
    'testimonials': '#9333ea',
    'contacts':     '#0d9488',
}

# Типы страниц у которых нет свободных секций
TYPED_PAGE_TYPES = {PageType.CONTACTS, PageType.NEWS, PageType.GALLERY}


class SectionInline(SortableInlineAdminMixin, StackedInline):
    """
    Инлайн секций с drag-and-drop по полю order.
    Показывается только для страниц типа default.
    """
    model           = Section
    form            = SectionAdminForm
    extra           = 0
    fields          = ['type', 'title', 'is_visible', 'data_preview_inline']
    readonly_fields = ['data_preview_inline']

    @admin.display(description='Данные секции')
    def data_preview_inline(self, obj):
        """Цветной бейдж и краткий превью содержимого секции."""
        if not obj.pk or not obj.data:
            return '—'
        color = SECTION_BADGE_COLORS.get(obj.type, '#94a3b8')
        badge = format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_type_display(),
        )
        snippets = []
        for key, val in list(obj.data.items())[:3]:
            if isinstance(val, list):
                snippets.append(f'{key}: [{len(val)} элем.]')
            elif isinstance(val, str) and val:
                snippets.append(f'{key}: {val[:50]}')
        preview = ' · '.join(snippets)
        return format_html('{} &nbsp; {}', badge, preview)


@admin.register(Page)
class PageAdmin(SortableAdminBase, ModelAdmin):
    list_display        = ['title', 'slug', 'page_type', 'is_published', 'order']
    list_editable       = ['is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'page_type', 'is_published', 'order'],
        }),
        ('SEO', {
            'fields': ['seo_title', 'seo_desc'],
            'classes': ['collapse'],
        }),
    ]

    def get_inlines(self, request, obj=None):
        """
        Инлайн секций скрывается для contacts, news_list, gallery —
        у этих страниц фиксированная структура без свободных секций.
        """
        if obj and obj.page_type in TYPED_PAGE_TYPES:
            return []
        return [SectionInline]


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    form          = SectionAdminForm
    list_display  = ['type_badge', '__str__', 'order', 'is_visible']
    list_filter   = ['type', 'page']
    list_editable = ['order', 'is_visible']
    ordering      = ['page', 'order']

    def get_fieldsets(self, request, obj=None):
        """
        Базовые поля + поля содержимого для существующей типизированной секции.
        При создании новой секции поля содержимого не показываются —
        нужно сначала выбрать тип и сохранить.
        """
        base = [(None, {'fields': ['page', 'type', 'title', 'order', 'is_visible']})]
        if obj and obj.type in SECTION_FORM_MAP:
            typed_fields = list(SECTION_FORM_MAP[obj.type].base_fields.keys())
            base.append(('Содержимое секции', {'fields': typed_fields, 'classes': ['wide']}))
        return base

    @admin.display(description='Тип')
    def type_badge(self, obj):
        color = SECTION_BADGE_COLORS.get(obj.type, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_type_display(),
        )
    
    def get_form(self, request, obj=None, **kwargs):
        # Отключаем проверку полей — типизированные поля добавляются
        # динамически в SectionAdminForm.__init__ и не известны модели
        kwargs['fields'] = None
        return super().get_form(request, obj, **kwargs)