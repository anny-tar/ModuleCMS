from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
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

TYPED_PAGE_TYPES = {PageType.CONTACTS, PageType.NEWS, PageType.GALLERY}


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display        = ['title', 'slug', 'page_type', 'is_published']
    list_editable       = []
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {
            'fields':      ['title', 'slug', 'page_type', 'is_published'],
            'description': 'Чтобы сменить тип страницы — удалите текущую и создайте новую.',
        }),
        ('SEO', {
            'fields':  ['seo_title', 'seo_desc'],
            'classes': ['collapse'],
        }),
    ]

    def get_readonly_fields(self, request, obj=None):
        # При редактировании тип страницы нельзя менять
        if obj:
            return ['page_type']
        return []

    def get_inlines(self, request, obj=None):
        return []

    def save_model(self, request, obj, form, change):
        # При создании назначаем уникальный order
        if not change:
            from django.db.models import Max
            max_order = Page.objects.aggregate(m=Max('order'))['m']
            obj.order = (max_order + 1) if max_order is not None else 0
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pages'] = Page.objects.all().order_by('order', 'title')
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            page = Page.objects.get(pk=object_id)
            if page.page_type not in TYPED_PAGE_TYPES:
                sections = page.sections.order_by('order')
                sections_data = []
                for s in sections:
                    snippets = []
                    for key, val in list(s.data.items())[:2]:
                        if isinstance(val, list):
                            snippets.append(f'{len(val)} элем.')
                        elif isinstance(val, str) and val:
                            snippets.append(val[:40])
                    sections_data.append({
                        'id':         s.pk,
                        'title':      s.title,
                        'type_label': s.get_type_display(),
                        'color':      SECTION_BADGE_COLORS.get(s.type, '#94a3b8'),
                        'preview':    ' · '.join(snippets),
                        'edit_url':   reverse('admin:pages_section_change', args=[s.pk]),
                        'delete_url': reverse('admin:pages_section_delete', args=[s.pk]),
                    })
                extra_context['sections_data']   = sections_data
                extra_context['add_section_url'] = (
                    reverse('admin:pages_section_add') + f'?page={object_id}'
                )
        except Page.DoesNotExist:
            pass
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    form          = SectionAdminForm
    list_display  = ['type_badge', '__str__', 'page', 'is_visible']
    list_filter   = ['type', 'page']
    ordering      = ['page', 'order']

    def get_readonly_fields(self, request, obj=None):
        # При редактировании тип секции нельзя менять
        if obj:
            return ['type']
        return []

    def get_fieldsets(self, request, obj=None):
        current_type = obj.type if obj else request.POST.get('type')
        base = [(None, {
            'fields':      ['page', 'type', 'title', 'is_visible'],
        })]
        if current_type and current_type in SECTION_FORM_MAP:
            typed_fields = list(SECTION_FORM_MAP[current_type].base_fields.keys())
            base.append(('Содержимое секции', {'fields': typed_fields, 'classes': ['wide']}))
        return base

    def get_form(self, request, obj=None, **kwargs):
        kwargs['fields'] = None
        form_class   = super().get_form(request, obj, **kwargs)
        current_type = obj.type if obj else request.POST.get('type')

        class PatchedSectionForm(form_class):
            def __init__(self_, *args, **kwargs_):
                instance = kwargs_.get('instance')
                if instance and current_type and instance.type != current_type:
                    instance.type = current_type
                super().__init__(*args, **kwargs_)

        return PatchedSectionForm

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        page_id = request.GET.get('page')
        if page_id:
            initial['page'] = page_id
        return initial

    def save_model(self, request, obj, form, change):
        # При создании назначаем уникальный order для данной страницы
        if not change and obj.page_id:
            from django.db.models import Max
            max_order = Section.objects.filter(page=obj.page).aggregate(m=Max('order'))['m']
            obj.order = (max_order + 1) if max_order is not None else 0
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return HttpResponseRedirect(
                reverse('admin:pages_page_change', args=[obj.page_id])
            )
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return HttpResponseRedirect(
                reverse('admin:pages_page_change', args=[obj.page_id])
            )
        return super().response_add(request, obj, post_url_continue)

    @admin.display(description='Тип')
    def type_badge(self, obj):
        color = SECTION_BADGE_COLORS.get(obj.type, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color,
            obj.get_type_display(),
        )