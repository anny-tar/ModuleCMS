from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Theme, Font, SiteSettings


@admin.register(Theme)
class ThemeAdmin(ModelAdmin):
    list_display = ['name', 'primary', 'background', 'surface', 'accent', 'text', 'is_custom']


@admin.register(Font)
class FontAdmin(ModelAdmin):
    list_display = ['name', 'google_font_name', 'fallback', 'is_custom']


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ['site_name', 'active_theme', 'active_font', 'home_slug']

    def has_add_permission(self, request):
        # Запрет создания второй записи настроек
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрет удаления единственной записи настроек
        return False