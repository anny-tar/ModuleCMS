import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .models import Page, Section


def page_detail(request, slug):
    page     = get_object_or_404(Page, slug=slug, is_published=True)
    sections = page.sections.filter(is_visible=True).order_by('order')

    template_map = {
        'default':   'pages/page_default.html',
        'contacts':  'pages/page_contacts.html',
        'news_list': 'pages/page_news.html',
        'gallery':   'pages/page_gallery.html',
    }
    template = template_map.get(page.page_type, 'pages/page_default.html')
    context  = {'page': page, 'sections': sections}

    if page.page_type == 'news_list':
        context = _news_context(request, context)
    elif page.page_type == 'contacts':
        context = _contacts_context(context)
    elif page.page_type == 'gallery':
        context = _gallery_context(context)

    return render(request, template, context)


@require_POST
@staff_member_required
def section_sort(request):
    """Сохраняет новый порядок секций."""
    try:
        data = json.loads(request.body)
        ids  = data.get('ids', [])
        for index, section_id in enumerate(ids):
            Section.objects.filter(pk=section_id).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
@staff_member_required
def page_sort(request):
    """Сохраняет новый порядок страниц."""
    try:
        data = json.loads(request.body)
        ids  = data.get('ids', [])
        for index, page_id in enumerate(ids):
            Page.objects.filter(pk=page_id).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


def _news_context(request, context):
    from news.models import Article, Category
    articles      = Article.objects.filter(is_published=True)
    categories    = Category.objects.all()
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


def _contacts_context(context):
    from appearance.models import SiteSettings
    context.update({'settings': SiteSettings.get()})
    return context