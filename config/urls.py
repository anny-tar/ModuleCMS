from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from config.cms_views import cms_toggle, cms_sort
from pages.views import section_fields, media_url, media_list


class HomeRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        from pages.models import Page
        page = Page.objects.filter(is_published=True).order_by('order').first()
        return f'/{page.slug}/' if page else '/admin/'


urlpatterns = [
    # Admin AJAX-эндпоинты — все под /admin/ чтобы браузер слал запросы туда же
    path('admin/cms-toggle/', cms_toggle, name='cms_toggle'),
    path('admin/cms-sort/', cms_sort, name='cms_sort'),
    path('admin/section-fields/', section_fields, name='section_fields'),
    path('admin/media-url/', media_url, name='media_url'),
    path('admin/media-list/', media_list, name='media_list'),
    path('admin/', admin.site.urls),
    path('', HomeRedirectView.as_view()),
    path('', include('news.urls')),
    path('', include('gallery.urls')),
    path('', include('leads.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)