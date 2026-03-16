"""
Базовый миксин для команд наполнения демо-данными.
Содержит общую логику очистки БД и создания пользователей.
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def clear_all():
    """Очищает все данные включая пользователей."""
    from pages.models import Page, Section
    from news.models import Article, Category
    from gallery.models import Album, Photo
    from leads.models import LeadSubmission
    from appearance.models import Theme, Font, SiteSettings

    LeadSubmission.objects.all().delete()
    Photo.objects.all().delete()
    Album.objects.all().delete()
    Article.objects.all().delete()
    Category.objects.all().delete()
    Section.objects.all().delete()
    Page.objects.all().delete()
    SiteSettings.objects.all().delete()
    Font.objects.all().delete()
    Theme.objects.all().delete()
    User.objects.all().delete()


def create_users():
    """
    Создаёт четырёх пользователей:
    - admin      / admin1234    — суперпользователь
    - director   / director1234 — суперпользователь (руководитель)
    - manager    / manager1234  — группа Менеджер
    - editor     / editor1234   — группа Контент-редактор
    """
    from django.contrib.auth.models import Group

    admin = User.objects.create_superuser(
        username='admin',
        password='admin1234',
        first_name='Администратор',
        email='admin@example.com',
    )

    director = User.objects.create_superuser(
        username='director',
        password='director1234',
        first_name='Руководитель',
        email='director@example.com',
    )

    manager = User.objects.create_user(
        username='manager',
        password='manager1234',
        first_name='Менеджер',
        email='manager@example.com',
    )
    try:
        manager.groups.add(Group.objects.get(name='Менеджер'))
    except Group.DoesNotExist:
        pass

    editor = User.objects.create_user(
        username='editor',
        password='editor1234',
        first_name='Редактор',
        email='editor@example.com',
    )
    try:
        editor.groups.add(Group.objects.get(name='Контент-редактор'))
    except Group.DoesNotExist:
        pass

    return admin, director, manager, editor


def create_appearance(primary, background, surface, accent, text, font_name, font_google):
    """Создаёт 6 тем, 6 шрифтов, возвращает активную тему и шрифт."""
    from appearance.models import Theme, Font

    themes_data = [
        {'name': 'Основная',     'primary': primary,    'background': background, 'surface': surface,    'accent': accent,    'text': text},
        {'name': 'Изумрудный',   'primary': '#059669',  'background': '#ffffff',  'surface': '#f0fdf4',  'accent': '#047857', 'text': '#1e293b'},
        {'name': 'Тёмный',       'primary': '#6366f1',  'background': '#0f172a',  'surface': '#1e293b',  'accent': '#818cf8', 'text': '#f1f5f9'},
        {'name': 'Оранжевый',    'primary': '#ea580c',  'background': '#ffffff',  'surface': '#fff7ed',  'accent': '#c2410c', 'text': '#1c1917'},
        {'name': 'Бирюзовый',    'primary': '#0891b2',  'background': '#ffffff',  'surface': '#f0f9ff',  'accent': '#0e7490', 'text': '#0c1a2e'},
        {'name': 'Серый',        'primary': '#374151',  'background': '#f9fafb',  'surface': '#e5e7eb',  'accent': '#1f2937', 'text': '#111827'},
    ]
    active_theme = None
    for i, d in enumerate(themes_data):
        t = Theme.objects.create(**d)
        if i == 0:
            active_theme = t

    fonts_data = [
        {'name': font_name,          'google_font_name': font_google,       'fallback': 'sans-serif'},
        {'name': 'Roboto',           'google_font_name': 'Roboto',          'fallback': 'sans-serif'},
        {'name': 'Inter',            'google_font_name': 'Inter',           'fallback': 'sans-serif'},
        {'name': 'Montserrat',       'google_font_name': 'Montserrat',      'fallback': 'sans-serif'},
        {'name': 'Open Sans',        'google_font_name': 'Open+Sans',       'fallback': 'sans-serif'},
        {'name': 'Playfair Display', 'google_font_name': 'Playfair+Display','fallback': 'serif'},
    ]
    active_font = None
    for i, d in enumerate(fonts_data):
        f = Font.objects.create(**d)
        if i == 0:
            active_font = f

    return active_theme, active_font