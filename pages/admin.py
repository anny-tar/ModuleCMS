from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Page, Section
from .forms import (HeroSectionForm, TextSectionForm,
                    CountersSectionForm, CardsSectionForm,
                    TeamSectionForm, StepsSectionForm,
                    TableSectionForm, ChartPieSectionForm,
                    FormSectionForm, FaqSectionForm,
                    TestimonialsSectionForm)

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


class SectionInline(admin.StackedInline):
    model  = Section
    extra  = 0
    fields = ['type', 'title', 'order', 'is_visible', 'data']


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display        = ['title', 'slug', 'page_type', 'is_published', 'order']
    list_editable       = ['is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    inlines             = [SectionInline]


@admin.register(Section)
class SectionAdmin(ModelAdmin):
    list_display  = ['__str__', 'type', 'order', 'is_visible']
    list_filter   = ['type', 'page']
    list_editable = ['order', 'is_visible']

    def get_form(self, request, obj=None, **kwargs):
        # Подбор формы по типу секции при редактировании существующей
        if obj and obj.type in SECTION_FORM_MAP:
            kwargs['fields'] = ['page', 'type', 'title', 'order', 'is_visible', 'data']
        return super().get_form(request, obj, **kwargs)