from pages.models import Page


def navigation(request):
    # Все опубликованные страницы сортируются по полю order
    pages = Page.objects.filter(is_published=True).order_by('order')
    return {'nav_pages': pages}