from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline
from adminsortable2.admin import SortableInlineAdminMixin
from .models import Page, Section
from .forms import (
    HeroSectionForm, TextSectionForm,
    CountersSectionForm, CardsSectionForm,
    TeamSectionForm, StepsSectionForm,
    TableSectionForm, ChartPieSectionForm,
    FormSectionForm, FaqSectionForm,
    TestimonialsSectionForm,
)

# Соответствие типа секции и формы для неё
SECTION_FORM_MAP = {
    'hero':         HeroSectionForm,
    'text':         TextSectionForm,
    'counters':     CountersSectionForm,
    'cards':        CardsSectionForm,
    'team':         TeamSectionForm,
    'steps':        StepsSectionForm,
    'table':        TableSectionForm,
    'chart_pie':    ChartPieSectionForm,
    'form':         FormSectionForm,
    'faq':          FaqSectionForm,
    'testimonials': TestimonialsSectionForm,
}

# Цвета бейджей для каждого типа секции
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


class SectionInline(SortableInlineAdminMixin, StackedInline):
    """
    Инлайн секций со drag-and-drop сортировкой.
    Поле order используется adminsortable2 для хранения позиции.
    """
    model           = Section
    extra           = 0
    # order скрыт — управляется перетаскиванием
    fields          = ['type', 'title', 'is_visible', 'data_preview_inline', 'data']
    readonly_fields = ['data_preview_inline']

    @admin.display(description='Превью данных')
    def data_preview_inline(self, obj):
        """Показывает краткое содержимое секции прямо в инлайне."""
        if not obj.pk or not obj.data:
            return '—'
        color = SECTION_BADGE_COLORS.get(obj.type, '#94a3b8')
        badge = format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_type_display(),
        )
        # Кратко показываем первые ключи данных
        snippets = []
        for key, val in list(obj.data.items())[:3]:
            if isinstance(val, list):
                snippets.append(f'{key}: [{len(val)} элем.]')
            elif isinstance(val, str) and val:
                snippets.append(f'{key}: {val[:40]}')
        preview_text = ' &nbsp;·&nbsp; '.join(snippets) if snippets else ''
        return format_html('{} &nbsp; {}', badge, format_html(preview_text))


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display        = ['title', 'slug', 'page_type', 'is_published', 'order']
    list_editable       = ['is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    inlines             = [SectionInline]
    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'page_type', 'is_published', 'order'],
        }),
        ('SEO', {
            'fields': ['seo_title', 'seo_desc'],
            'classes': ['collapse'],
        }),
    ]


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    list_display  = ['type_badge', '__str__', 'order', 'is_visible']
    list_filter   = ['type', 'page']
    list_editable = ['order', 'is_visible']
    ordering      = ['page', 'order']

    @admin.display(description='Тип')
    def type_badge(self, obj):
        """Цветной бейдж типа секции в списке."""
        color = SECTION_BADGE_COLORS.get(obj.type, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_type_display(),
        )

    def get_form(self, request, obj=None, **kwargs):
        """
        При редактировании существующей секции подставляется
        типизированная форма вместо сырого JSONField.
        Поле data скрывается — данные вводятся через поля формы.
        """
        if obj and obj.type in SECTION_FORM_MAP:
            # Показываем служебные поля + поля типизированной формы
            kwargs['fields'] = ['page', 'type', 'title', 'order', 'is_visible']
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        """Добавляет блок с полями типизированной формы для редактирования."""
        base = [
            (None, {
                'fields': ['page', 'type', 'title', 'order', 'is_visible'],
            }),
        ]
        if obj and obj.type in SECTION_FORM_MAP:
            form_class = SECTION_FORM_MAP[obj.type]
            typed_fields = list(form_class.base_fields.keys())
            base.append((
                'Содержимое секции',
                {'fields': typed_fields, 'classes': ['wide']},
            ))
        else:
            # При создании новой секции — сырой JSONField
            base[0][1]['fields'].append('data')
        return base

    def get_initial_for_field(self, field, field_name):
        """Заглушка — начальные значения заполняются через changeform_view."""
        return super().get_initial_for_field(field, field_name)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """
        Подставляет начальные значения из obj.data в поля типизированной формы
        при открытии страницы редактирования.
        """
        if object_id:
            try:
                obj = Section.objects.get(pk=object_id)
                if obj.type in SECTION_FORM_MAP and request.method == 'GET':
                    # Разворачиваем сохранённый JSON в initial для GET-запроса
                    extra_context = extra_context or {}
                    extra_context['section_initial'] = obj.data
            except Section.DoesNotExist:
                pass
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        При сохранении типизированной секции собирает поля формы обратно в JSON.
        """
        if obj.type in SECTION_FORM_MAP:
            form_class = SECTION_FORM_MAP[obj.type]
            typed_fields = list(form_class.base_fields.keys())
            # Собираем только поля, относящиеся к типизированной форме
            raw = {f: form.cleaned_data.get(f) for f in typed_fields
                   if f in form.cleaned_data}
            # Если форма поддерживает to_data() — используем её
            typed_form = form_class(data=raw)
            typed_form.is_valid()
            if hasattr(typed_form, 'to_data'):
                obj.data = typed_form.to_data()
            else:
                obj.data = {k: v for k, v in raw.items() if v is not None}
        super().save_model(request, obj, form, change)