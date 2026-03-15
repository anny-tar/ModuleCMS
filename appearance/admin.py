from django.contrib import admin
from .models import Theme, Font, SiteSettings


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary', 'background', 'surface', 'accent', 'text', 'is_custom']


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ['name', 'google_font_name', 'fallback', 'is_custom']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'active_theme', 'active_font', 'home_slug']

    def has_add_permission(self, request):
        # Запрет создания второй записи настроек
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрет удаления единственной записи настроек
        return False