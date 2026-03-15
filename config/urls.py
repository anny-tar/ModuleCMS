from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/glavnaya/', permanent=False)),
    # Конкретные маршруты — всегда выше универсального <slug:slug>/
    path('', include('news.urls')),
    path('', include('gallery.urls')),
    path('', include('leads.urls')),
    # Универсальный маршрут страниц — всегда последний
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)