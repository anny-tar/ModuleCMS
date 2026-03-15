from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from appearance.models import SiteSettings


def get_home_url():
    return f'/{SiteSettings.get().home_slug}/'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=get_home_url(), permanent=False)),
    path('', include('news.urls')),
    path('', include('gallery.urls')),
    path('', include('leads.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)