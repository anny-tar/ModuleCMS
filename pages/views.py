import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_GET
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from .models import Page, Section, SECTION_ICONS
from .forms import SECTION_FORM_MAP


def page_detail(request, slug):
    is_preview = request.GET.get('preview') == '1' and request.user.is_staff

    # В режиме превью разрешаем смотреть неопубликованные страницы
    if is_preview:
        page = get_object_or_404(Page, slug=slug)
    else:
        page = get_object_or_404(Page, slug=slug, is_published=True)

    sections = page.sections.filter(is_visible=True).order_by('order')

    template_map = {
        'default':   'pages/page_default.html',
        'contacts':  'pages/page_contacts.html',
        'news_list': 'pages/page_news.html',
        'gallery':   'pages/page_gallery.html',
    }
    template = template_map.get(page.page_type, 'pages/page_default.html')

    # В режиме превью подменяем data → draft_data для секций у которых есть черновик
    if is_preview:
        for section in sections:
            if section.draft_data is not None:
                section.data = section.draft_data

    context  = {'page': page, 'sections': sections, 'is_preview': is_preview}

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


@require_POST
@staff_member_required
def section_preview(request):
    """
    AJAX: рендерит секцию через реальный Django-шаблон и возвращает HTML-фрагмент.

    POST /admin/section-preview/
    Body JSON: {"type": "cards", "title": "Наши услуги", "data": {...}}

    Ответ: {"html": "<section class=...>...</section>"}
    """
    try:
        body = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid json'}, status=400)

    section_type = body.get('type', '')
    title        = body.get('title', '')
    raw_data     = body.get('data', {})

    form_class = SECTION_FORM_MAP.get(section_type)
    if not form_class:
        return JsonResponse({'error': 'unknown type'}, status=400)

    # Прогоняем через to_data() — та же логика что при реальном сохранении
    clean_data = form_class().to_data(raw_data)

    # Временный объект секции (не сохраняется в БД)
    section        = Section.__new__(Section)
    section.pk     = 0
    section.type   = section_type
    section.title  = title
    section.data   = clean_data

    template_name = f'sections/{section_type}.html'
    try:
        html = render_to_string(template_name, {'section': section, 'data': clean_data}, request=request)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'html': html})


@require_POST
@staff_member_required
def section_draft_save(request):
    """
    AJAX: сохраняет черновик секции без публикации основных данных.

    POST /admin/section-draft-save/
    Body JSON: {"section_id": 42, "type": "cards", "title": "...", "data": {...}}

    Ответ: {"ok": true, "preview_url": "/my-page/?preview=1#section-42"}
    """
    try:
        body = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid json'}, status=400)

    section_id   = body.get('section_id')
    section_type = body.get('type', '')
    raw_data     = body.get('data', {})

    if not section_id:
        return JsonResponse({'error': 'section_id required'}, status=400)

    try:
        section = Section.objects.select_related('page').get(pk=section_id)
    except Section.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    form_class = SECTION_FORM_MAP.get(section_type)
    if not form_class:
        return JsonResponse({'error': 'unknown type'}, status=400)

    section.draft_data = form_class().to_data(raw_data)
    section.save(update_fields=['draft_data'])

    preview_url = f'/{section.page.slug}/?preview=1#section-{section_id}'
    return JsonResponse({'ok': True, 'preview_url': preview_url})


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