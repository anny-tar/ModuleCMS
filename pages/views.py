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
    AJAX: возвращает поля формы для выбранного типа секции и текущие данные.

    GET /pages/section/fields/?type=hero&section_id=42

    Ответ:
    {
        "fields": [
            {"name": "heading", "label": "Заголовок", "type": "text",
             "value": "Привет", "required": true, "help_text": ""},
            ...
        ],
        "icon": "🖼️"
    }
    """
    section_type = request.GET.get('type', '')
    section_id   = request.GET.get('section_id')

    form_class = SECTION_FORM_MAP.get(section_type)
    if not form_class:
        return JsonResponse({'error': 'unknown type'}, status=400)

    # Если редактируем существующую секцию — подставляем текущие данные
    current_data = {}
    if section_id:
        try:
            section = Section.objects.get(pk=section_id)
            if section.type == section_type and section.data:
                current_data = form_class.from_data(section.data)
        except Section.DoesNotExist:
            pass

    # Собираем описание полей для JS
    fields_info = []
    for name, field in form_class.base_fields.items():
        widget     = field.widget
        field_type = _widget_type(widget)
        fields_info.append({
            'name':      name,
            'label':     str(field.label or name),
            'type':      field_type,
            'value':     current_data.get(name, ''),
            'required':  field.required,
            'help_text': str(field.help_text or ''),
        })

    return JsonResponse({
        'fields': fields_info,
        'icon':   SECTION_ICONS.get(section_type, '📄'),
    })


def _widget_type(widget):
    """Определяет тип input-а по классу виджета Django."""
    from django import forms as dj_forms
    if isinstance(widget, dj_forms.Textarea):
        return 'textarea'
    if isinstance(widget, dj_forms.HiddenInput):
        return 'hidden'
    if isinstance(widget, dj_forms.CheckboxInput):
        return 'checkbox'
    if isinstance(widget, dj_forms.NumberInput):
        return 'number'
    if isinstance(widget, dj_forms.EmailInput):
        return 'email'
    if isinstance(widget, dj_forms.URLInput):
        return 'url'
    return 'text'


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
        ids  = data.get('ids', [])\
        
        for index, page_id in enumerate(ids):
            Page.objects.filter(pk=page_id).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Вспомогательные функции для контекста
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