"""
Команда для полной очистки базы данных.
Удаляет все пользовательские данные, сохраняя суперпользователей.

Использование:
    python manage.py clear_data
    python manage.py clear_data --yes  # без подтверждения
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Очищает все пользовательские данные из базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes', action='store_true',
            help='Пропустить подтверждение',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            confirm = input(
                'Все данные будут удалены. Суперпользователи сохранятся. '
                'Продолжить? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write('Отменено.')
                return

        from pages.models import Page, Section
        from news.models import Article, Category
        from gallery.models import Album, Photo
        from leads.models import LeadSubmission
        from appearance.models import Theme, Font, SiteSettings

        counts = {
            'Заявки':      LeadSubmission.objects.count(),
            'Фото':        Photo.objects.count(),
            'Альбомы':     Album.objects.count(),
            'Статьи':      Article.objects.count(),
            'Категории':   Category.objects.count(),
            'Секции':      Section.objects.count(),
            'Страницы':    Page.objects.count(),
            'Настройки':   SiteSettings.objects.count(),
            'Шрифты':      Font.objects.count(),
            'Темы':        Theme.objects.count(),
        }

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

        for model, count in counts.items():
            if count:
                self.stdout.write(f'  Удалено {model}: {count}')

        self.stdout.write(self.style.SUCCESS('База данных очищена.'))