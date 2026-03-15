from django.shortcuts import get_object_or_404, render
from .models import Page


def page_detail(request, slug):
    page     = get_object_or_404(Page, slug=slug, is_published=True)
    sections = page.sections.filter(is_visible=True).order_by('order')

    template_map = {
        'default':  'pages/page_default.html',
        'contacts': 'pages/page_contacts.html',
        'news_list':'pages/page_news.html',
        'gallery':  'pages/page_gallery.html',
    }
    template = template_map.get(page.page_type, 'pages/page_default.html')

    # Базовый контекст — одинаков для всех типов
    context = {'page': page, 'sections': sections}

    # Дополнительный контекст для типизированных страниц
    if page.page_type == 'news_list':
        context = _news_context(request, context)
    elif page.page_type == 'gallery':
        context = _gallery_context(context)

    return render(request, template, context)


def _news_context(request, context):
    from news.models import Article, Category
    articles   = Article.objects.filter(is_published=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    context.update({'articles': articles, 'categories': categories})
    return context


def _gallery_context(context):
    from gallery.models import Album
    albums = Album.objects.filter(is_published=True)
    context.update({'albums': albums})
    return context