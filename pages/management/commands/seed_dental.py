"""
Команда: python manage.py seed_dental

Демо-данные для сайта стоматологической клиники «Белая улыбка».

📸 Необходимые фотографии (положить в media_files/, затем python manage.py import_media):
  hero-dental.jpg       — главный баннер, современный светлый кабинет или улыбающийся пациент
  doctor-1.jpg          — врач 1, портрет в белом халате, квадратный обрез
  doctor-2.jpg          — врач 2, портрет в белом халате, квадратный обрез
  doctor-3.jpg          — врач 3, портрет в белом халате, квадратный обрез
  clinic-interior.jpg   — интерьер клиники / зал ожидания
  before-after.jpg      — результаты лечения (опционально)

  После импорта замените None на нужный ID в полях photo_id / image_id.
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


USERS = [
    {
        'username': 'admin', 'password': 'admin123',
        'email': 'admin@dental-smile.ru',
        'first_name': 'Администратор', 'last_name': '',
        'is_superuser': True, 'is_staff': True, 'role': 'Суперпользователь',
    },
    {
        'username': 'manager', 'password': 'manager123',
        'email': 'admin-clinic@dental-smile.ru',
        'first_name': 'Ирина', 'last_name': 'Соколова',
        'is_superuser': False, 'is_staff': True, 'role': 'Администратор клиники',
    },
]

NEWS_CATEGORIES = ['Новости клиники', 'Акции', 'Полезные статьи', 'Технологии']

ARTICLES = [
    {
        'title': 'Новая технология имплантации All-on-4',
        'category': 'Технологии',
        'announce': 'Теперь полное восстановление зубного ряда за один визит.',
        'content': '<p>Клиника «Белая улыбка» освоила технологию имплантации <strong>All-on-4</strong>. '
                   'Четыре имплантата обеспечивают надёжную основу для полного протеза уже в день операции.</p>'
                   '<p>Процедура занимает 3–4 часа, а пациент уходит с постоянными зубами в тот же день.</p>',
        'is_published': True,
    },
    {
        'title': 'Акция на профессиональную чистку зубов',
        'category': 'Акции',
        'announce': 'В апреле — скидка 30% на ультразвуковую чистку и Air Flow.',
        'content': '<p>Весь апрель профессиональная гигиена полости рта со скидкой 30%. '
                   'Ультразвуковая чистка + Air Flow + полировка = 2 100 ₽ вместо 3 000 ₽.</p>'
                   '<p>Записаться можно по телефону или через форму на сайте.</p>',
        'is_published': True,
    },
    {
        'title': 'Как правильно чистить зубы',
        'category': 'Полезные статьи',
        'announce': 'Разбираем технику чистки зубов, которую рекомендуют стоматологи.',
        'content': '<p>Большинство людей чистят зубы неправильно. Рассказываем, как делать это правильно.</p>'
                   '<p><strong>Время:</strong> не менее 2 минут дважды в день. '
                   '<strong>Движения:</strong> круговые и выметающие, не горизонтальные.</p>',
        'is_published': True,
    },
    {
        'title': 'Открытие нового кабинета детской стоматологии',
        'category': 'Новости клиники',
        'announce': 'Детский кабинет с игровой зоной и добрыми врачами.',
        'content': '<p>Мы открыли специализированный кабинет для маленьких пациентов от 3 лет. '
                   'Яркий интерьер, игровая зона и врачи с опытом работы с детьми сделают '
                   'визит к стоматологу комфортным.</p>',
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
                    'heading': 'Здоровые зубы — красивая улыбка',
                    'subheading': 'Современная стоматология без боли. Принимаем взрослых и детей от 3 лет.',
                    'align': 'left', 'buttons': 'two',
                    'btn1_text': 'Записаться на приём', 'btn1_url': '/kontakty/',
                    'btn2_text': 'Наши услуги', 'btn2_url': '/uslugi/',
                    'bg_mode': 'image_light', 'image_id': None,  # → hero-dental.jpg
                },
            },
            {
                'type': 'counters', 'title': '', 'order': 1,
                'data': {
                    'items': [
                        {'value': '15+',    'label': 'Лет работы'},
                        {'value': '12 000', 'label': 'Пациентов'},
                        {'value': '8',      'label': 'Врачей'},
                        {'value': '4.9',    'label': 'Рейтинг на Яндексе'},
                    ],
                },
            },
            {
                'type': 'cards', 'title': 'Почему нас выбирают', 'order': 2,
                'data': {
                    'items': [
                        {'icon': '😌', 'title': 'Лечение без боли',
                         'text': '<p>Современные анестетики и седация. Никакого страха и дискомфорта.</p>'},
                        {'icon': '🔬', 'title': 'Современное оборудование',
                         'text': '<p>Цифровой рентген, 3D-томография, лазерное лечение.</p>'},
                        {'icon': '👨‍⚕️', 'title': 'Опытные врачи',
                         'text': '<p>Все врачи с опытом от 8 лет и регулярным повышением квалификации.</p>'},
                        {'icon': '💳', 'title': 'Рассрочка 0%',
                         'text': '<p>Оплата в рассрочку без процентов на срок до 12 месяцев.</p>'},
                    ],
                },
            },
            {
                'type': 'steps', 'title': 'Как попасть к нам', 'order': 3,
                'data': {
                    'direction': 'horizontal',
                    'items': [
                        {'title': 'Запись',         'description': '<p>Позвоните или оставьте заявку онлайн.</p>'},
                        {'title': 'Консультация',   'description': '<p>Врач осмотрит и составит план лечения.</p>'},
                        {'title': 'Лечение',        'description': '<p>Проводим лечение по согласованному плану.</p>'},
                        {'title': 'Наблюдение',     'description': '<p>Напомним о профилактическом осмотре.</p>'},
                    ],
                },
            },
            {
                'type': 'testimonials', 'title': 'Отзывы пациентов', 'order': 4,
                'data': {
                    'items': [
                        {'name': 'Елена В.', 'role': 'Пациент с 2019 года',
                         'text': '<p>Наконец нашла клинику, где не страшно! Врачи внимательные, '
                                 'всё объясняют. Сделала имплантацию — очень довольна результатом.</p>',
                         'photo_id': None},
                        {'name': 'Андрей М.', 'role': 'Пациент',
                         'text': '<p>Привожу сюда всю семью, включая детей. Ребёнок теперь '
                                 'сам просится к стоматологу — это о многом говорит!</p>',
                         'photo_id': None},
                        {'name': 'Ольга К.', 'role': 'Пациент с 2021 года',
                         'text': '<p>Поставили виниры — работой очень довольна. '
                                 'Результат превзошёл ожидания, улыбаюсь теперь на все фото.</p>',
                         'photo_id': None},
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Записаться на приём', 'order': 5,
                'data': {
                    'description': 'Оставьте заявку — администратор перезвонит и подберёт удобное время',
                    'button_text': 'Записаться',
                    'success_message': 'Заявка принята! Перезвоним в течение 30 минут.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text', 'label': 'Ваше имя',    'required': True},
                        {'name': 'field_2', 'type': 'tel',  'label': 'Телефон',     'required': True},
                        {'name': 'field_3', 'type': 'text', 'label': 'Услуга',      'required': False},
                    ],
                },
            },
        ],
    },
    {
        'title': 'Услуги', 'slug': 'uslugi',
        'page_type': 'default', 'order': 1,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Наши услуги',
                    'subheading': 'Полный спектр стоматологических услуг для взрослых и детей',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'cards', 'title': 'Направления', 'order': 1,
                'data': {
                    'items': [
                        {'icon': '🦷', 'title': 'Терапия',
                         'text': '<p>Лечение кариеса, пульпита, периодонтита. Реставрация зубов.</p>'},
                        {'icon': '🔧', 'title': 'Хирургия',
                         'text': '<p>Удаление зубов любой сложности, имплантация, костная пластика.</p>'},
                        {'icon': '😬', 'title': 'Ортодонтия',
                         'text': '<p>Брекеты, элайнеры, ретейнеры для детей и взрослых.</p>'},
                        {'icon': '✨', 'title': 'Эстетика',
                         'text': '<p>Виниры, люминиры, отбеливание, художественная реставрация.</p>'},
                        {'icon': '🦴', 'title': 'Имплантация',
                         'text': '<p>Имплантаты Nobel, Straumann. Протоколы All-on-4, All-on-6.</p>'},
                        {'icon': '🧸', 'title': 'Детская стоматология',
                         'text': '<p>Лечение молочных и постоянных зубов. Профилактика с 3 лет.</p>'},
                    ],
                },
            },
            {
                'type': 'table', 'title': 'Прайс-лист', 'order': 2,
                'data': {
                    'style': 'zebra',
                    'headers': ['Услуга', 'Цена от'],
                    'rows': [
                        ['Консультация врача',              'Бесплатно'],
                        ['Лечение кариеса',                 '3 500 ₽'],
                        ['Профессиональная чистка',         '3 000 ₽'],
                        ['Удаление зуба (простое)',         '2 500 ₽'],
                        ['Имплантация (под ключ)',          '45 000 ₽'],
                        ['Виниры (1 шт.)',                  '18 000 ₽'],
                        ['Брекеты (полная система)',        '65 000 ₽'],
                        ['Отбеливание Zoom 4',             '18 000 ₽'],
                    ],
                },
            },
            {
                'type': 'faq', 'title': 'Частые вопросы', 'order': 3,
                'data': {
                    'icon_style': 'arrow',
                    'items': [
                        {'question': 'Больно ли лечить зубы?',
                         'answer': '<p>Нет. Мы используем современные анестетики, которые полностью '
                                   'устраняют болевые ощущения. При необходимости возможна седация.</p>'},
                        {'question': 'Принимаете ли вы детей?',
                         'answer': '<p>Да, принимаем детей от 3 лет. У нас есть специализированный '
                                   'детский кабинет с игровой зоной.</p>'},
                        {'question': 'Есть ли рассрочка?',
                         'answer': '<p>Да, предоставляем беспроцентную рассрочку на срок до 12 месяцев '
                                   'на все виды лечения стоимостью от 10 000 ₽.</p>'},
                        {'question': 'Как записаться на приём?',
                         'answer': '<p>Позвоните по телефону, напишите в WhatsApp или оставьте заявку '
                                   'на сайте — перезвоним в течение 30 минут.</p>'},
                        {'question': 'Работаете ли вы по выходным?',
                         'answer': '<p>Да, принимаем в субботу с 9:00 до 16:00. '
                                   'В воскресенье — только экстренная помощь.</p>'},
                    ],
                },
            },
        ],
    },
    {
        'title': 'Врачи', 'slug': 'vrachi',
        'page_type': 'default', 'order': 2,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Наши врачи',
                    'subheading': 'Профессионалы с опытом от 8 лет',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'team', 'title': '', 'order': 1,
                'data': {
                    'items': [
                        {'name': 'Михаил Зубов', 'position': 'Главный врач, хирург-имплантолог',
                         'description': '<p>Стаж 18 лет. Специализация: имплантация, костная пластика. '
                                        'Сертификат Nobel Biocare.</p>',
                         'photo_id': None},  # → doctor-1.jpg
                        {'name': 'Анна Белова', 'position': 'Терапевт-эстет',
                         'description': '<p>Стаж 12 лет. Художественная реставрация, виниры, '
                                        'отбеливание. Постоянный участник конференций.</p>',
                         'photo_id': None},  # → doctor-2.jpg
                        {'name': 'Сергей Прямов', 'position': 'Ортодонт',
                         'description': '<p>Стаж 10 лет. Лечение брекетами и элайнерами Invisalign. '
                                        'Принимает детей и взрослых.</p>',
                         'photo_id': None},  # → doctor-3.jpg
                    ],
                },
            },
            {
                'type': 'counters', 'title': 'Достижения', 'order': 2,
                'data': {
                    'items': [
                        {'value': '3',   'label': 'Кандидата медицинских наук'},
                        {'value': '40+', 'label': 'Сертификатов повышения квалификации'},
                        {'value': '8',   'label': 'Лет минимальный стаж'},
                        {'value': '15',  'label': 'Конференций в год'},
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
        'title': 'Контакты', 'slug': 'kontakty',
        'page_type': 'default', 'order': 4,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Запишитесь на приём',
                    'subheading': 'Перезвоним в течение 30 минут и подберём удобное время',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'contacts', 'title': 'Контактная информация', 'order': 1,
                'data': {
                    'layout': 'none',
                    'map_url': '', 'map_label': '', 'map_description': '',
                    'items': [
                        {'type': 'phone',   'label': 'Запись на приём', 'value': '+7 (495) 500-20-10', 'description': 'Пн–Пт 8:00–21:00'},
                        {'type': 'phone',   'label': 'WhatsApp',        'value': '+7 (926) 500-20-10', 'description': ''},
                        {'type': 'email',   'label': 'Email',           'value': 'hello@dental-smile.ru', 'description': ''},
                        {'type': 'address', 'label': 'Адрес',           'value': 'Москва, ул. Садовая, 15, этаж 2', 'description': 'Вход со двора, домофон 201'},
                        {'type': 'hours',   'label': 'Режим работы',    'value': 'Пн–Пт 8:00–21:00, Сб 9:00–16:00', 'description': ''},
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Онлайн-запись', 'order': 2,
                'data': {
                    'description': 'Оставьте заявку — перезвоним и подберём удобное время',
                    'button_text': 'Записаться',
                    'success_message': 'Заявка принята! Перезвоним в течение 30 минут.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text', 'label': 'Ваше имя',    'required': True},
                        {'name': 'field_2', 'type': 'tel',  'label': 'Телефон',     'required': True},
                        {'name': 'field_3', 'type': 'text', 'label': 'Услуга',      'required': False},
                        {'name': 'field_4', 'type': 'text', 'label': 'Удобное время', 'required': False},
                    ],
                },
            },
        ],
    },
]

LEADS = [
    {'data': {'Ваше имя': 'Елена Васильева', 'Телефон': '+7 916 200-30-40', 'Услуга': 'Имплантация'}},
    {'data': {'Ваше имя': 'Андрей Морозов',  'Телефон': '+7 903 500-60-70', 'Услуга': 'Брекеты'}},
    {'data': {'Ваше имя': 'Ольга Крылова',   'Телефон': '+7 926 800-90-10', 'Услуга': 'Виниры'}},
]


class Command(BaseCommand):
    help = 'Заполняет базу данными стоматологической клиники «Белая улыбка»'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить базу перед заполнением')

    def handle(self, *args, **options):
        if options['clear']:
            from django.core.management import call_command
            call_command('clear_db', '--yes', '--keep-users')

        self.stdout.write(self.style.HTTP_INFO('\n🌱  Заполняем базу — Стоматология «Белая улыбка»\n'))
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
            self.stdout.write(f'   ✨ {lead["data"].get("Ваше имя")}')

    def _setup_settings(self):
        from appearance.models import SiteSettings, Theme
        self.stdout.write('⚙️  Настройки:')
        s = SiteSettings.get()
        s.site_name = 'Белая улыбка'; s.nav_mode = 'name_only'
        s.contact_phone = '+7 (495) 500-20-10'; s.contact_email = 'hello@dental-smile.ru'
        s.contact_address = 'Москва, ул. Садовая, 15'
        s.contact_hours = 'Пн–Пт 8:00–21:00, Сб 9:00–16:00'
        theme = Theme.objects.first()
        if theme: s.active_theme = theme
        s.save()
        self.stdout.write(f'   ✅ {s.site_name}')