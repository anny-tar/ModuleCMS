from django.shortcuts import get_object_or_404, render
from .models import Page


def page_detail(request, slug):
    # Возвращает только опубликованные страницы
    page     = get_object_or_404(Page, slug=slug, is_published=True)
    sections = page.sections.filter(is_visible=True).order_by('order')

    # Выбор шаблона в зависимости от типа страницы
    template_map = {
        'default':  'pages/page_default.html',
        'contacts': 'pages/page_contacts.html',
        'news_list':'pages/page_news.html',
        'gallery':  'pages/page_gallery.html',
    }
    template = template_map.get(page.page_type, 'pages/page_default.html')

    return render(request, template, {'page': page, 'sections': sections})