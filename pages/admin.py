from django.contrib import admin
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Page, Section, SECTION_ICONS
from .forms import SectionAdminForm


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display  = ['title', 'slug', 'page_type', 'is_published', 'order']
    list_filter   = ['page_type', 'is_published']
    search_fields = ['title', 'slug']
    ordering      = ['order', 'title']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pages'] = Page.objects.all().order_by('order', 'title')
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            page     = Page.objects.get(pk=object_id)
            sections = page.sections.order_by('order')
            sections_data = []
            for s in sections:
                sections_data.append({
                    'id':         s.pk,
                    'icon':       s.icon(),
                    'title':      s.title or s.get_type_display(),
                    'type_label': s.get_type_display(),
                    'is_visible': s.is_visible,
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
    form         = SectionAdminForm
    list_display = ['icon_and_type', 'page', 'order', 'is_visible']
    list_filter  = ['type', 'is_visible', 'page']
    ordering     = ['page', 'order']

    @admin.display(description='Тип секции')
    def icon_and_type(self, obj):
        """Колонка с иконкой и названием типа в списке секций."""
        return format_html(
            '<span style="font-size:1.1em;margin-right:6px;">{}</span>{}',
            obj.icon(),
            obj.get_type_display(),
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        page_id = request.GET.get('page')
        if page_id:
            initial['page'] = page_id
        return initial

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            section = Section.objects.get(pk=object_id)
            page    = section.page
            extra_context['preview_url'] = f'/{page.slug}/#section-{object_id}'
        except Section.DoesNotExist:
            pass
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """При создании секции — ставим order в конец."""
        if not change and obj.page_id:
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