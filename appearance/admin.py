from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Theme, Font, SiteSettings


class ColorInput(forms.TextInput):
    """
    Виджет, совмещающий стандартный color picker браузера
    с текстовым полем для ввода hex-кода вручную.
    """
    input_type = 'color'

    def __init__(self, attrs=None):
        default_attrs = {'style': 'width:60px;height:36px;padding:2px;cursor:pointer;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ThemeAdminForm(forms.ModelForm):
    """Форма темы с color picker для каждого цветового поля."""
    class Meta:
        model   = Theme
        fields  = '__all__'
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
    list_display = ['name', 'color_swatches', 'is_custom']

    @admin.display(description='Цвета')
    def color_swatches(self, obj):
        """Отображает пять цветовых кружков темы в списке."""
        swatches = ''.join(
            format_html(
                '<span title="{}" style="display:inline-block;width:20px;height:20px;'
                'border-radius:50%;background:{};margin-right:4px;'
                'border:1px solid #e2e8f0;"></span>',
                label, color,
            )
            for label, color in [
                ('Primary',    obj.primary),
                ('Background', obj.background),
                ('Surface',    obj.surface),
                ('Accent',     obj.accent),
                ('Text',       obj.text),
            ]
        )
        return format_html(swatches)


@admin.register(Font)
class FontAdmin(ModelAdmin):
    list_display = ['name', 'google_font_name', 'fallback', 'is_custom']


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ['site_name', 'active_theme', 'active_font', 'home_slug']
    fieldsets = [
        (None, {
            'fields': ['site_name', 'active_theme', 'active_font', 'home_slug'],
        }),
        ('Контактные данные', {
            'fields': ['contact_address', 'contact_phone',
                       'contact_email', 'contact_hours', 'contact_map_url'],
        }),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False