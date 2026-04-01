from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from unfold.admin import ModelAdmin
from .models import Theme, Font, SiteSettings


class ColorInput(forms.TextInput):
    """Виджет color picker браузера для цветовых полей темы."""
    input_type = 'color'

    def __init__(self, attrs=None):
        default_attrs = {'style': 'width:60px;height:36px;padding:2px;cursor:pointer;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ThemeAdminForm(forms.ModelForm):
    """Форма темы с color picker. Поле is_custom скрыто — управляется программно."""
    class Meta:
        model   = Theme
        exclude = ['is_custom']
        widgets = {
            'primary':    ColorInput(),
            'background': ColorInput(),
            'surface':    ColorInput(),
            'accent':     ColorInput(),
            'text':       ColorInput(),
        }


@admin.register(Theme)
class ThemeAdmin(ModelAdmin):
    form         = ThemeAdminForm
    list_display = ['name', 'color_swatches']

    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.is_custom:
            return ['name', 'primary', 'background', 'surface', 'accent', 'text']
        return []

    def has_change_permission(self, request, obj=None):
        if obj and not obj.is_custom:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.is_custom:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_custom = True
        super().save_model(request, obj, form, change)

    @admin.display(description='Цвета')
    def color_swatches(self, obj):
        parts = []
        for label, color in [
            ('Primary',    obj.primary),
            ('Background', obj.background),
            ('Surface',    obj.surface),
            ('Accent',     obj.accent),
            ('Text',       obj.text),
        ]:
            parts.append(format_html(
                '<span title="{}" style="display:inline-block;width:20px;height:20px;'
                'border-radius:50%;background:{};margin-right:4px;'
                'border:1px solid #e2e8f0;"></span>',
                label, color,
            ))
        return mark_safe(''.join(str(p) for p in parts))


class FontAdminForm(forms.ModelForm):
    """Форма шрифта. Поле is_custom скрыто — управляется программно."""
    class Meta:
        model   = Font
        exclude = ['is_custom']


@admin.register(Font)
class FontAdmin(ModelAdmin):
    form         = FontAdminForm
    list_display = ['name', 'google_font_name', 'fallback']

    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.is_custom:
            return ['name', 'google_font_name', 'fallback', 'custom_file']
        return []

    def has_change_permission(self, request, obj=None):
        if obj and not obj.is_custom:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.is_custom:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_custom = True
        super().save_model(request, obj, form, change)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ['site_name', 'active_theme', 'active_font', 'nav_mode']
    fieldsets = [
        (None, {
            'fields': ['site_name', 'active_theme', 'active_font'],
        }),
        ('Логотип и навигация', {
            'fields': ['logo', 'favicon', 'nav_mode'],
        }),
        ('Контакты для навигационного меню и футера', {
            'fields': ['contact_address', 'contact_phone',
                       'contact_email', 'contact_hours'],
        }),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False