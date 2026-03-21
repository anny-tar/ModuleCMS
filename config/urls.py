from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from config.cms_views import cms_toggle, cms_sort


class HomeRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        from pages.models import Page
        page = Page.objects.filter(is_published=True).order_by('order').first()
        return f'/{page.slug}/' if page else '/admin/'


urlpatterns = [
    path('admin/cms-toggle/', cms_toggle, name='cms_toggle'),
    path('admin/cms-sort/', cms_sort, name='cms_sort'),
    path('admin/', admin.site.urls),
    path('', HomeRedirectView.as_view()),
    path('', include('news.urls')),
    path('', include('gallery.urls')),
    path('', include('leads.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)