from .models import SiteSettings


def site_settings(request):
    # Настройки сайта доступны во всех шаблонах
    settings = SiteSettings.get()
    return {'site_settings': settings}