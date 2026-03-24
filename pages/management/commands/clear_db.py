"""
Команда: python manage.py clear_db

Полная очистка базы данных проекта:
- Удаляет все страницы, секции, новости, галерею, заявки
- Удаляет всех пользователей кроме суперпользователей
- Сбрасывает настройки сайта к значениям по умолчанию
- НЕ удаляет темы, шрифты и медиафайлы (они не контент)
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Очищает базу данных: страницы, секции, новости, галерею, заявки, пользователей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Пропустить подтверждение',
        )
        parser.add_argument(
            '--keep-users',
            action='store_true',
            help='Не удалять пользователей',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  Внимание! Это действие удалит ВСЕ данные из базы.\n'
                '   Страницы, секции, новости, галерея, заявки будут удалены.\n'
            ))
            confirm = input('Введите "yes" для подтверждения: ')
            if confirm.strip().lower() != 'yes':
                self.stdout.write(self.style.ERROR('Отменено.'))
                return

        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(self.style.HTTP_INFO('🗑  Начинаем очистку базы данных...'))
        self.stdout.write('─' * 50)

        with transaction.atomic():
            self._clear_leads()
            self._clear_pages()
            self._clear_news()
            self._clear_gallery()
            if not options['keep_users']:
                self._clear_users()
            self._reset_site_settings()

        self.stdout.write('─' * 50)
        self.stdout.write(self.style.SUCCESS('✅  База данных очищена успешно!\n'))

    def _clear_leads(self):
        from leads.models import LeadSubmission
        count = LeadSubmission.objects.count()
        LeadSubmission.objects.all().delete()
        self.stdout.write(f'   🗑  Заявки:      удалено {count}')

    def _clear_pages(self):
        from pages.models import Section, Page
        s_count = Section.objects.count()
        p_count = Page.objects.count()
        Section.objects.all().delete()
        Page.objects.all().delete()
        self.stdout.write(f'   🗑  Секции:      удалено {s_count}')
        self.stdout.write(f'   🗑  Страницы:    удалено {p_count}')

    def _clear_news(self):
        from news.models import Article, Category
        a_count = Article.objects.count()
        c_count = Category.objects.count()
        Article.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(f'   🗑  Статьи:      удалено {a_count}')
        self.stdout.write(f'   🗑  Категории:   удалено {c_count}')

    def _clear_gallery(self):
        from gallery.models import Album, Photo
        ph_count = Photo.objects.count()
        al_count = Album.objects.count()
        Photo.objects.all().delete()
        Album.objects.all().delete()
        self.stdout.write(f'   🗑  Фотографии:  удалено {ph_count}')
        self.stdout.write(f'   🗑  Альбомы:     удалено {al_count}')

    def _clear_users(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Удаляем только не-суперпользователей
        non_super = User.objects.filter(is_superuser=False)
        count = non_super.count()
        non_super.delete()
        super_count = User.objects.filter(is_superuser=True).count()
        self.stdout.write(f'   🗑  Пользователи: удалено {count} (суперпользователи сохранены: {super_count})')

    def _reset_site_settings(self):
        from appearance.models import SiteSettings
        SiteSettings.objects.filter(pk=1).update(
            site_name='Онлайн-школа',
            contact_address='',
            contact_phone='',
            contact_email='',
            contact_hours='',
            contact_map_url='',
        )
        self.stdout.write('   🔄  Настройки сайта: сброшены')