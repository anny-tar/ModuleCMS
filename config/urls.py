from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


class HomeRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Импорт и вызов только в момент запроса, не при старте
        from appearance.models import SiteSettings
        return f'/{SiteSettings.get().home_slug}/'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeRedirectView.as_view()),
    path('', include('news.urls')),
    path('', include('gallery.urls')),
    path('', include('leads.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)