from pages.models import Page


def navigation(request):
    pages = Page.objects.filter(is_published=True).order_by('order')

    nav_items = []
    for page in pages:
        anchors = []
        if page.page_type == 'default':
            for section in page.sections.filter(is_visible=True, title__gt='').order_by('order'):
                anchors.append({
                    'title': section.title,
                    'url':   f'/{page.slug}/#section-{section.pk}',
                })
        nav_items.append({
            'title':   page.title,
            'url':     f'/{page.slug}/',
            'anchors': anchors,
        })

    return {'nav_items': nav_items}