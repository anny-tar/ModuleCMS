import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required


# Разрешённые модели и поля для toggle
TOGGLE_MAP = {
    'page':    ('pages.Page',                   'is_published'),
    'section': ('pages.Section',                'is_visible'),
    'article': ('news.Article',                 'is_published'),
    'album':   ('gallery.Album',                'is_published'),
    'photo':   ('gallery.Photo',               'is_published'),
    'lead':    ('leads.LeadSubmission',         'is_viewed'),
}

# Разрешённые модели для сортировки
SORT_MAP = {
    'page':     'pages.Page',
    'section':  'pages.Section',
    'album':    'gallery.Album',
    'photo':    'gallery.Photo',
}


@require_POST
@staff_member_required
def cms_toggle(request):
    try:
        data  = json.loads(request.body)
        model_key = data.get('model')
        obj_id    = int(data.get('id'))
        value     = bool(data.get('value'))

        if model_key not in TOGGLE_MAP:
            return JsonResponse({'ok': False, 'error': 'unknown model'}, status=400)

        app_model, field = TOGGLE_MAP[model_key]
        app_label, model_name = app_model.split('.')

        from django.apps import apps
        Model = apps.get_model(app_label, model_name)
        updated = Model.objects.filter(pk=obj_id).update(**{field: value})

        if updated == 0:
            return JsonResponse({'ok': False, 'error': 'not found'}, status=404)

        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
@staff_member_required
def cms_sort(request):
    """Универсальная сортировка по model + ids."""
    try:
        data      = json.loads(request.body)
        model_key = data.get('model')
        ids       = data.get('ids', [])

        if model_key not in SORT_MAP:
            return JsonResponse({'ok': False, 'error': 'unknown model'}, status=400)

        from django.apps import apps
        app_label, model_name = SORT_MAP[model_key].split('.')
        Model = apps.get_model(app_label, model_name)

        for index, obj_id in enumerate(ids):
            Model.objects.filter(pk=obj_id).update(order=index)

        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

