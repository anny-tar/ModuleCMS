from django.contrib import admin
from .models import Page, Section


class SectionInline(admin.TabularInline):
    model  = Section
    extra  = 0
    # Поля, видимые в строчном редакторе внутри страницы
    fields = ['type', 'title', 'order', 'is_visible']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display   = ['title', 'slug', 'page_type', 'is_published', 'order']
    list_editable  = ['is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    inlines        = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'type', 'order', 'is_visible']
    list_filter   = ['type', 'page']
    list_editable = ['order', 'is_visible']