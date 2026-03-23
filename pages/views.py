import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.admin.views.decorators import staff_member_required
from .models import Page, Section, SECTION_ICONS
from .forms import SECTION_FORM_MAP


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


@require_GET
@staff_member_required
def section_fields(request):
    """
    AJAX: возвращает схему полей для выбранного типа секции + текущие значения.

    GET /admin/section-fields/?type=text&section_id=42

    Ответ:
    {
        "fields": [
            {
                "name": "content", "label": "Содержимое",
                "type": "quill",  "value": "<p>...</p>",
                "required": false, "help_text": "",
                "depends_on": null
            }
        ],
        "icon": "📝"
    }
    """
    section_type = request.GET.get('type', '')
    section_id   = request.GET.get('section_id')

    form_class = SECTION_FORM_MAP.get(section_type)
    if not form_class:
        return JsonResponse({'error': 'unknown type'}, status=400)

    # Текущие значения если редактируем существующую секцию
    current_values = {}
    if section_id:
        try:
            section = Section.objects.get(pk=section_id)
            if section.type == section_type and section.data:
                current_values = form_class.from_data(section.data)
        except Section.DoesNotExist:
            pass

    # Берём схему из get_schema() и подставляем текущие значения
    schema = form_class.get_schema()
    for field in schema:
        name = field.get('name')
        if name and name in current_values:
            field['value'] = current_values[name]
        elif 'value' not in field:
            field['value'] = ''

    return JsonResponse({
        'fields': schema,
        'icon':   SECTION_ICONS.get(section_type, '📄'),
    })


@require_GET
@staff_member_required
def media_list(request):
    from media_library.models import MediaFile
    q         = request.GET.get('q', '').strip()
    only_type = request.GET.get('type', 'image')
    qs = MediaFile.objects.filter(media_type=only_type).order_by('-uploaded_at')
    if q:
        qs = qs.filter(original_name__icontains=q)
    qs = qs[:200]
    items = [{'id': m.pk, 'name': m.original_name, 'url': m.url} for m in qs]
    return JsonResponse({'items': items})


@require_GET
@staff_member_required
def media_url(request):
    """
    AJAX: возвращает URL медиафайла по ID — для превью без сохранения.

    GET /admin/media-url/?id=42
    → {"url": "/media/uploads/photo.jpg", "name": "photo.jpg"}
    """
    file_id = request.GET.get('id')
    if not file_id:
        return JsonResponse({'error': 'no id'}, status=400)
    try:
        from media_library.models import MediaFile
        media = MediaFile.objects.get(pk=file_id)
        return JsonResponse({'url': media.file.url, 'name': str(media)})
    except Exception:
        return JsonResponse({'error': 'not found'}, status=404)


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


# ---------------------------------------------------------------------------
# Вспомогательные функции контекста
# ---------------------------------------------------------------------------

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