"""
Команда: python manage.py seed_factory

Демо-данные для сайта производственной компании «МеталлПро».

📸 Необходимые фотографии (положить в media_files/, затем python manage.py import_media):
  hero-factory.jpg      — главный баннер, производственный цех или оборудование, горизонтальный
  production-1.jpg      — фото производства / цеха
  production-2.jpg      — готовая продукция или процесс изготовления
  cert-1.jpg            — сертификат качества (опционально)
  worker-1.jpg          — сотрудник / инженер, портрет, квадратный обрез
  worker-2.jpg          — сотрудник / инженер, портрет, квадратный обрез

  После импорта замените None на нужный ID в полях photo_id / image_id.
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


USERS = [
    {
        'username': 'admin', 'password': 'admin123',
        'email': 'admin@metallpro.ru',
        'first_name': 'Администратор', 'last_name': '',
        'is_superuser': True, 'is_staff': True, 'role': 'Суперпользователь',
    },
    {
        'username': 'manager', 'password': 'manager123',
        'email': 'manager@metallpro.ru',
        'first_name': 'Сергей', 'last_name': 'Николаев',
        'is_superuser': False, 'is_staff': True, 'role': 'Менеджер',
    },
]

NEWS_CATEGORIES = ['Новости компании', 'Производство', 'Сертификаты и награды', 'Отраслевые новости']

ARTICLES = [
    {
        'title': 'Запуск новой производственной линии',
        'category': 'Производство',
        'announce': 'В марте 2025 года введена в эксплуатацию новая автоматизированная линия.',
        'content': '<p>Компания МеталлПро завершила монтаж и пусконаладку новой производственной линии '
                   'по обработке металлопроката. Мощность линии — до 500 тонн в месяц.</p>'
                   '<p>Это позволит сократить сроки выполнения заказов на 30% и расширить ассортимент продукции.</p>',
        'is_published': True,
    },
    {
        'title': 'Получен сертификат ISO 9001:2015',
        'category': 'Сертификаты и награды',
        'announce': 'Система менеджмента качества компании успешно прошла сертификацию.',
        'content': '<p>По результатам аудита, проведённого независимым органом по сертификации, '
                   'компании МеталлПро выдан сертификат соответствия <strong>ISO 9001:2015</strong>.</p>'
                   '<p>Сертификат подтверждает высокий уровень контроля качества на всех этапах производства.</p>',
        'is_published': True,
    },
    {
        'title': 'Участие в выставке «Металл-Экспо 2025»',
        'category': 'Новости компании',
        'announce': 'Представили новые разработки на крупнейшей отраслевой выставке.',
        'content': '<p>С 11 по 14 ноября компания МеталлПро приняла участие в международной выставке '
                   '«Металл-Экспо 2025» в Москве. На стенде были представлены образцы продукции '
                   'и новые технологические решения.</p>',
        'is_published': True,
    },
    {
        'title': 'Увеличение объёмов производства в 2025 году',
        'category': 'Производство',
        'announce': 'По итогам года объём производства вырос на 25% по сравнению с прошлым годом.',
        'content': '<p>Благодаря модернизации оборудования и оптимизации производственных процессов '
                   'компании удалось увеличить выпуск продукции до 4 800 тонн в год.</p>',
        'is_published': True,
    },
]

PAGES = [
    {
        'title': 'Главная', 'slug': 'glavnaia',
        'page_type': 'default', 'order': 0,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Производство металлоконструкций под заказ',
                    'subheading': 'Работаем с 2005 года. Собственное производство, гарантия качества, доставка по России.',
                    'align': 'left', 'buttons': 'two',
                    'btn1_text': 'Запросить цену', 'btn1_url': '/kontakty/',
                    'btn2_text': 'О компании', 'btn2_url': '/o-kompanii/',
                    'bg_mode': 'image_dark', 'image_id': None,  # → hero-factory.jpg
                },
            },
            {
                'type': 'counters', 'title': 'Компания в цифрах', 'order': 1,
                'data': {
                    'items': [
                        {'value': '20+',    'label': 'Лет на рынке'},
                        {'value': '4 800',  'label': 'Тонн продукции в год'},
                        {'value': '350+',   'label': 'Постоянных клиентов'},
                        {'value': '48 ч',   'label': 'Среднее время заказа'},
                    ],
                },
            },
            {
                'type': 'cards', 'title': 'Наши преимущества', 'order': 2,
                'data': {
                    'items': [
                        {'icon': '🏭', 'title': 'Собственное производство',
                         'text': '<p>Полный цикл — от проектирования до отгрузки готовой продукции.</p>'},
                        {'icon': '✅', 'title': 'Контроль качества',
                         'text': '<p>Сертификат ISO 9001. Каждая партия проходит входной и выходной контроль.</p>'},
                        {'icon': '🚚', 'title': 'Доставка по России',
                         'text': '<p>Собственный автопарк и логистические партнёры по всей стране.</p>'},
                        {'icon': '📐', 'title': 'Нестандартные заказы',
                         'text': '<p>Изготавливаем по чертежам заказчика любой сложности.</p>'},
                    ],
                },
            },
            {
                'type': 'steps', 'title': 'Как сделать заказ', 'order': 3,
                'data': {
                    'direction': 'horizontal',
                    'items': [
                        {'title': 'Заявка',        'description': '<p>Оставьте заявку или позвоните нам.</p>'},
                        {'title': 'Расчёт',        'description': '<p>Просчитаем стоимость в течение 2 часов.</p>'},
                        {'title': 'Производство',  'description': '<p>Изготовим в согласованные сроки.</p>'},
                        {'title': 'Доставка',      'description': '<p>Доставим на объект или самовывоз.</p>'},
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Запросить коммерческое предложение', 'order': 4,
                'data': {
                    'description': 'Опишите задачу — ответим с расчётом в течение 2 часов',
                    'button_text': 'Отправить запрос',
                    'success_message': 'Заявка принята! Свяжемся в течение 2 часов.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',     'label': 'Компания / ФИО', 'required': True},
                        {'name': 'field_2', 'type': 'tel',      'label': 'Телефон',        'required': True},
                        {'name': 'field_3', 'type': 'email',    'label': 'Email',          'required': False},
                        {'name': 'field_4', 'type': 'textarea', 'label': 'Описание заказа','required': True},
                    ],
                },
            },
        ],
    },
    {
        'title': 'О компании', 'slug': 'o-kompanii',
        'page_type': 'default', 'order': 1,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'О компании МеталлПро',
                    'subheading': 'Надёжный производитель металлоконструкций с 2005 года',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'text', 'title': 'История компании', 'order': 1,
                'data': {
                    'content': '<p>Компания МеталлПро основана в 2005 году в Екатеринбурге. '
                               'Начинали с небольшого цеха и трёх сотрудников, сегодня — это '
                               'современное предприятие площадью 8 000 м² с коллективом 120 человек.</p>'
                               '<p>Специализируемся на производстве металлоконструкций, балок, ферм, '
                               'ограждений и нестандартных изделий по чертежам заказчика.</p>'
                               '<p>Среди наших клиентов — строительные компании, промышленные предприятия '
                               'и государственные объекты по всей России.</p>',
                },
            },
            {
                'type': 'counters', 'title': '', 'order': 2,
                'data': {
                    'items': [
                        {'value': '120',    'label': 'Сотрудников'},
                        {'value': '8 000',  'label': 'м² производства'},
                        {'value': '15',     'label': 'Единиц оборудования'},
                        {'value': 'ISO',    'label': '9001:2015'},
                    ],
                },
            },
            {
                'type': 'team', 'title': 'Руководство', 'order': 3,
                'data': {
                    'items': [
                        {'name': 'Виктор Громов', 'position': 'Генеральный директор',
                         'description': '<p>20 лет в металлообработке. Основатель компании.</p>',
                         'photo_id': None},  # → worker-1.jpg
                        {'name': 'Наталья Орлова', 'position': 'Главный инженер',
                         'description': '<p>К.т.н., 15 лет опыта в проектировании конструкций.</p>',
                         'photo_id': None},  # → worker-2.jpg
                    ],
                },
            },
        ],
    },
    {
        'title': 'Продукция', 'slug': 'produktsia',
        'page_type': 'default', 'order': 2,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Наша продукция',
                    'subheading': 'Производим металлоконструкции любой сложности',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'cards', 'title': 'Виды продукции', 'order': 1,
                'data': {
                    'items': [
                        {'icon': '🏗️', 'title': 'Металлоконструкции',
                         'text': '<p>Балки, колонны, фермы, рамы для строительства и промышленности.</p>'},
                        {'icon': '🔩', 'title': 'Закладные детали',
                         'text': '<p>Анкерные болты, пластины, арматурные выпуски.</p>'},
                        {'icon': '🚧', 'title': 'Ограждения',
                         'text': '<p>Заборы, перила, ограждения лестниц и балконов.</p>'},
                        {'icon': '⚙️', 'title': 'Нестандартные изделия',
                         'text': '<p>Изготовление по чертежам и техническому заданию заказчика.</p>'},
                        {'icon': '🏠', 'title': 'Каркасы зданий',
                         'text': '<p>Лёгкие металлические конструкции для быстровозводимых зданий.</p>'},
                        {'icon': '🛤️', 'title': 'Лестницы и пандусы',
                         'text': '<p>Маршевые, винтовые, пожарные лестницы из металла.</p>'},
                    ],
                },
            },
            {
                'type': 'table', 'title': 'Технические характеристики', 'order': 2,
                'data': {
                    'style': 'first_col',
                    'headers': ['Параметр', 'Значение'],
                    'rows': [
                        ['Материалы',          'Сталь Ст3, 09Г2С, нержавейка AISI 304/316'],
                        ['Точность резки',     '± 0,5 мм'],
                        ['Максимальная длина', 'до 12 000 мм'],
                        ['Толщина металла',    'от 1 до 80 мм'],
                        ['Покрытие',           'Грунтовка, порошковая покраска, оцинковка'],
                        ['Срок изготовления',  'от 2 рабочих дней'],
                    ],
                },
            },
            {
                'type': 'faq', 'title': 'Часто задаваемые вопросы', 'order': 3,
                'data': {
                    'icon_style': 'plus',
                    'items': [
                        {'question': 'Работаете ли вы с физическими лицами?',
                         'answer': '<p>Да, принимаем заказы как от юридических, так и от физических лиц.</p>'},
                        {'question': 'Есть ли возможность самовывоза?',
                         'answer': '<p>Да, самовывоз с нашего склада в Екатеринбурге бесплатный.</p>'},
                        {'question': 'Предоставляете ли вы проектную документацию?',
                         'answer': '<p>Да, наши инженеры разрабатывают чертежи и расчёты по запросу.</p>'},
                        {'question': 'Какова гарантия на продукцию?',
                         'answer': '<p>Даём гарантию 2 года на все виды продукции собственного производства.</p>'},
                    ],
                },
            },
        ],
    },
    {
        'title': 'Новости', 'slug': 'novosti',
        'page_type': 'news_list', 'order': 3,
    },
    {
        'title': 'Галерея', 'slug': 'galereya',
        'page_type': 'gallery', 'order': 4,
    },
    {
        'title': 'Контакты', 'slug': 'kontakty',
        'page_type': 'default', 'order': 5,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Контакты',
                    'subheading': 'Ответим на вопросы и рассчитаем стоимость заказа',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'contacts', 'title': 'Как с нами связаться', 'order': 1,
                'data': {
                    'layout': 'none',
                    'map_url': '', 'map_label': '', 'map_description': '',
                    'items': [
                        {'type': 'phone',   'label': 'Отдел продаж', 'value': '+7 (343) 200-10-20', 'description': 'Пн–Пт 8:00–18:00'},
                        {'type': 'phone',   'label': 'Технический отдел', 'value': '+7 (343) 200-10-21', 'description': ''},
                        {'type': 'email',   'label': 'Email',         'value': 'sales@metallpro.ru', 'description': ''},
                        {'type': 'address', 'label': 'Производство',  'value': 'Екатеринбург, ул. Промышленная, 45', 'description': ''},
                        {'type': 'hours',   'label': 'Режим работы',  'value': 'Пн–Пт 8:00–18:00, Сб 9:00–14:00', 'description': ''},
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Запрос на расчёт', 'order': 2,
                'data': {
                    'description': 'Опишите задачу — ответим с расчётом в течение 2 часов',
                    'button_text': 'Отправить запрос',
                    'success_message': 'Запрос получен! Свяжемся с вами в течение 2 часов.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',     'label': 'Компания / ФИО', 'required': True},
                        {'name': 'field_2', 'type': 'tel',      'label': 'Телефон',        'required': True},
                        {'name': 'field_3', 'type': 'textarea', 'label': 'Описание заказа','required': True},
                    ],
                },
            },
        ],
    },
]

LEADS = [
    {'data': {'Компания / ФИО': 'ООО СтройГрупп', 'Телефон': '+7 912 100-20-30', 'Описание заказа': 'Металлические фермы для склада 500м²'}},
    {'data': {'Компания / ФИО': 'ИП Захаров А.В.', 'Телефон': '+7 922 300-40-50', 'Описание заказа': 'Ограждение лестницы, нержавейка'}},
]


class Command(BaseCommand):
    help = 'Заполняет базу данными производственной компании «МеталлПро»'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить базу перед заполнением')

    def handle(self, *args, **options):
        if options['clear']:
            from django.core.management import call_command
            call_command('clear_db', '--yes', '--keep-users')

        self.stdout.write(self.style.HTTP_INFO('\n🌱  Заполняем базу — Производственная компания «МеталлПро»\n'))
        with transaction.atomic():
            self._create_users()
            self._create_pages()
            self._create_news()
            self._create_leads()
            self._setup_settings()
        self.stdout.write(self.style.SUCCESS('\n✅  Готово! http://127.0.0.1:8000/\n'))

    def _create_users(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.stdout.write('👤  Пользователи:')
        for u in USERS:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email = u['email']; user.first_name = u['first_name']
            user.last_name = u['last_name']; user.is_superuser = u['is_superuser']
            user.is_staff = u['is_staff']; user.set_password(u['password']); user.save()
            self.stdout.write(f'   {"✨" if created else "🔄"} {u["username"]} / {u["password"]}  ({u["role"]})')

    def _create_pages(self):
        from pages.models import Page, Section
        self.stdout.write('📄  Страницы:')
        for p in PAGES:
            page, created = Page.objects.get_or_create(slug=p['slug'])
            page.title = p['title']; page.page_type = p['page_type']
            page.order = p['order']; page.is_published = True; page.save()
            Section.objects.filter(page=page).delete()
            for s in p.get('sections', []):
                Section.objects.create(page=page, type=s['type'], title=s.get('title', ''),
                                       order=s['order'], is_visible=True, data=s.get('data', {}))
            self.stdout.write(f'   {"✨" if created else "🔄"} {page.title} ({len(p.get("sections", []))} секций)')

    def _create_news(self):
        from news.models import Category, Article
        self.stdout.write('📰  Новости:')
        cats = {}
        for name in NEWS_CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name)
            cats[name] = cat
        for a in ARTICLES:
            obj, created = Article.objects.get_or_create(title=a['title'])
            obj.category = cats.get(a['category']); obj.announce = a['announce']
            obj.content = a['content']; obj.is_published = a['is_published']
            obj.published_at = timezone.now(); obj.save()
            self.stdout.write(f'   {"✨" if created else "🔄"} {obj.title[:50]}')

    def _create_leads(self):
        from leads.models import LeadSubmission
        self.stdout.write('📬  Заявки:')
        for lead in LEADS:
            LeadSubmission.objects.create(section_id=1, data=lead['data'],
                                          ip_address=f'192.168.1.{random.randint(1,254)}')
            self.stdout.write(f'   ✨ {list(lead["data"].values())[0]}')

    def _setup_settings(self):
        from appearance.models import SiteSettings, Theme
        self.stdout.write('⚙️  Настройки:')
        s = SiteSettings.get()
        s.site_name = 'МеталлПро'; s.nav_mode = 'name_only'
        s.contact_phone = '+7 (343) 200-10-20'; s.contact_email = 'sales@metallpro.ru'
        s.contact_address = 'Екатеринбург, ул. Промышленная, 45'
        s.contact_hours = 'Пн–Пт 8:00–18:00'
        theme = Theme.objects.first()
        if theme: s.active_theme = theme
        s.save()
        self.stdout.write(f'   ✅ {s.site_name}')