"""
Команда: python manage.py seed_school

Демо-данные для сайта онлайн-школы «Старт».

📸 Необходимые фотографии (положить в media_files/, затем python manage.py import_media):
  hero-school.jpg       — главный баннер, светлый офис или ноутбук на столе, горизонтальный
  teacher-1.jpg         — преподаватель 1, портрет, квадратный обрез
  teacher-2.jpg         — преподаватель 2, портрет, квадратный обрез
  teacher-3.jpg         — преподаватель 3, портрет, квадратный обрез
  student-1.jpg         — студент/выпускник 1, портрет, квадратный обрез
  student-2.jpg         — студент/выпускник 2, портрет, квадратный обрез

  После импорта замените None на нужный ID в полях photo_id / image_id.
  ID файла виден в адресной строке при открытии записи в Медиабиблиотеке.
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


USERS = [
    {
        'username': 'admin', 'password': 'admin123',
        'email': 'admin@school-start.ru',
        'first_name': 'Администратор', 'last_name': '',
        'is_superuser': True, 'is_staff': True, 'role': 'Суперпользователь',
    },
    {
        'username': 'manager', 'password': 'manager123',
        'email': 'manager@school-start.ru',
        'first_name': 'Анна', 'last_name': 'Петрова',
        'is_superuser': False, 'is_staff': True, 'role': 'Менеджер контента',
    },
]

NEWS_CATEGORIES = ['Новости школы', 'Анонсы курсов', 'Истории успеха', 'Советы']

ARTICLES = [
    {
        'title': 'Открытие нового курса по Python',
        'category': 'Анонсы курсов',
        'announce': 'С 1 февраля стартует интенсивный курс по Python для начинающих.',
        'content': '<p>Мы рады сообщить об открытии нового курса <strong>Python с нуля</strong>. '
                   'Программа рассчитана на 3 месяца и включает 48 практических занятий.</p>'
                   '<p>Вас ждут: основы языка, работа с данными, создание веб-приложений и финальный проект.</p>',
        'is_published': True,
    },
    {
        'title': 'Наши выпускники устроились в Яндекс и Сбер',
        'category': 'Истории успеха',
        'announce': '15 выпускников получили офферы от ведущих IT-компаний.',
        'content': '<p>Мы гордимся нашими студентами! В этом квартале сразу 15 выпускников '
                   'получили предложения о работе от крупнейших технологических компаний.</p>'
                   '<p>Средняя зарплата наших выпускников составляет 120 000 рублей в месяц.</p>',
        'is_published': True,
    },
    {
        'title': 'День открытых дверей — 15 марта',
        'category': 'Новости школы',
        'announce': 'Приглашаем всех желающих на бесплатное мероприятие.',
        'content': '<p>15 марта в 18:00 состоится день открытых дверей онлайн-школы Старт.</p>'
                   '<p>Получите скидку 20% при записи в день мероприятия.</p>',
        'is_published': True,
    },
    {
        'title': 'Как выбрать первый язык программирования',
        'category': 'Советы',
        'announce': 'Разбираем плюсы и минусы популярных языков для начинающих.',
        'content': '<p>Один из самых частых вопросов — с чего начать? '
                   '<strong>Python</strong> — лучший выбор для большинства новичков.</p>',
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
                    'heading': 'Освойте IT-профессию за 3–6 месяцев',
                    'subheading': 'Практическое обучение от действующих специалистов. Помогаем найти первую работу.',
                    'align': 'left', 'buttons': 'two',
                    'btn1_text': 'Выбрать курс', 'btn1_url': '/kursy/',
                    'btn2_text': 'О школе', 'btn2_url': '/o-nas/',
                    'bg_mode': 'none', 'image_id': None,  # → hero-school.jpg
                },
            },
            {
                'type': 'counters', 'title': 'Наши результаты', 'order': 1,
                'data': {
                    'items': [
                        {'value': '1 200+', 'label': 'Выпускников'},
                        {'value': '87%',    'label': 'Трудоустроились'},
                        {'value': '18',     'label': 'Преподавателей'},
                        {'value': '4.9',    'label': 'Средняя оценка'},
                    ],
                },
            },
            {
                'type': 'cards', 'title': 'Почему выбирают нас', 'order': 2,
                'data': {
                    'items': [
                        {'icon': '🎯', 'title': 'Практика с первого дня',
                         'text': '<p>Никакой теории ради теории — сразу пишем код и делаем проекты.</p>'},
                        {'icon': '👨‍💼', 'title': 'Преподаватели-практики',
                         'text': '<p>Все преподаватели работают в IT-компаниях прямо сейчас.</p>'},
                        {'icon': '💼', 'title': 'Помощь с трудоустройством',
                         'text': '<p>Помогаем составить резюме и готовим к техническим собеседованиям.</p>'},
                        {'icon': '📱', 'title': 'Удобный формат',
                         'text': '<p>Учитесь в любое время — все материалы доступны 24/7.</p>'},
                    ],
                },
            },
            {
                'type': 'steps', 'title': 'Как проходит обучение', 'order': 3,
                'data': {
                    'direction': 'horizontal',
                    'items': [
                        {'title': 'Выбираете курс',   'description': '<p>Консультируемся и подбираем программу.</p>'},
                        {'title': 'Учитесь онлайн',   'description': '<p>Видеоуроки, практика, домашние задания.</p>'},
                        {'title': 'Делаете проект',   'description': '<p>Финальный проект для портфолио.</p>'},
                        {'title': 'Находите работу',  'description': '<p>Помогаем с резюме и собеседованиями.</p>'},
                    ],
                },
            },
            {
                'type': 'testimonials', 'title': 'Отзывы студентов', 'order': 4,
                'data': {
                    'items': [
                        {'name': 'Мария К.', 'role': 'Frontend-разработчик в Сбере',
                         'text': '<p>За 4 месяца с нуля до первой работы. Очень довольна!</p>',
                         'photo_id': None},  # → student-1.jpg
                        {'name': 'Алексей Т.', 'role': 'Python-разработчик',
                         'text': '<p>Нашёл работу на 40% выше предыдущей зарплаты. Рекомендую!</p>',
                         'photo_id': None},  # → student-2.jpg
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Запишитесь на бесплатную консультацию', 'order': 5,
                'data': {
                    'description': 'Ответим на все вопросы и поможем выбрать курс',
                    'button_text': 'Отправить заявку',
                    'success_message': 'Спасибо! Свяжемся в течение часа.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',  'label': 'Ваше имя', 'required': True},
                        {'name': 'field_2', 'type': 'tel',   'label': 'Телефон',  'required': True},
                        {'name': 'field_3', 'type': 'text',  'label': 'Какой курс интересует?', 'required': False},
                    ],
                },
            },
        ],
    },
    {
        'title': 'О нас', 'slug': 'o-nas',
        'page_type': 'default', 'order': 1,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'О школе Старт',
                    'subheading': 'Помогаем людям войти в IT с 2018 года',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'text', 'title': 'Наша история', 'order': 1,
                'data': {
                    'content': '<p>Школа Старт основана в 2018 году практикующими IT-специалистами. '
                               'Мы устали от теоретических курсов и создали школу, где обучение '
                               'строится вокруг реальных задач.</p>'
                               '<p>Каждый курс — это не лекции, а работа над проектами. '
                               'Наши выпускники устраиваются на работу в среднем через 2 месяца.</p>',
                },
            },
            {
                'type': 'team', 'title': 'Наши преподаватели', 'order': 2,
                'data': {
                    'items': [
                        {'name': 'Дмитрий Волков', 'position': 'Python, Backend',
                         'description': '<p>10 лет в разработке. Работал в Яндексе и Mail.ru.</p>',
                         'photo_id': None},  # → teacher-1.jpg
                        {'name': 'Екатерина Смирнова', 'position': 'Frontend, React',
                         'description': '<p>Senior Frontend в Тинькофф. Ведёт курсы 4 года.</p>',
                         'photo_id': None},  # → teacher-2.jpg
                        {'name': 'Артём Козлов', 'position': 'Data Science, ML',
                         'description': '<p>PhD в математике, Data Scientist в Сбере.</p>',
                         'photo_id': None},  # → teacher-3.jpg
                    ],
                },
            },
        ],
    },
    {
        'title': 'Курсы', 'slug': 'kursy',
        'page_type': 'default', 'order': 2,
        'sections': [
            {
                'type': 'hero', 'title': '', 'order': 0,
                'data': {
                    'heading': 'Наши курсы',
                    'subheading': 'Выберите направление и начните обучение уже сегодня',
                    'align': 'center', 'buttons': 'none',
                    'bg_mode': 'none', 'image_id': None,
                },
            },
            {
                'type': 'cards', 'title': 'Направления обучения', 'order': 1,
                'data': {
                    'items': [
                        {'icon': '🐍', 'title': 'Python-разработчик',
                         'text': '<p>3 месяца · от 0 до Junior</p><p>Backend, Django, REST API</p>'},
                        {'icon': '⚛️', 'title': 'Frontend-разработчик',
                         'text': '<p>4 месяца · от 0 до Junior</p><p>HTML, CSS, JavaScript, React</p>'},
                        {'icon': '📊', 'title': 'Data Analyst',
                         'text': '<p>3 месяца · от 0 до Junior</p><p>Python, SQL, Pandas</p>'},
                        {'icon': '🎨', 'title': 'UX/UI дизайнер',
                         'text': '<p>2 месяца · от 0 до Junior</p><p>Figma, прототипы, юзабилити</p>'},
                        {'icon': '🤖', 'title': 'Machine Learning',
                         'text': '<p>4 месяца · уровень Middle</p><p>scikit-learn, TensorFlow</p>'},
                        {'icon': '🔐', 'title': 'Кибербезопасность',
                         'text': '<p>3 месяца · от 0 до Junior</p><p>Основы ИБ, пентест, OWASP</p>'},
                    ],
                },
            },
            {
                'type': 'table', 'title': 'Сравнение курсов', 'order': 2,
                'data': {
                    'style': 'zebra',
                    'headers': ['Курс', 'Длительность', 'Формат', 'Цена'],
                    'rows': [
                        ['Python-разработчик',   '3 месяца', 'Онлайн', '45 000 ₽'],
                        ['Frontend-разработчик', '4 месяца', 'Онлайн', '55 000 ₽'],
                        ['Data Analyst',         '3 месяца', 'Онлайн', '40 000 ₽'],
                        ['UX/UI дизайнер',       '2 месяца', 'Онлайн', '35 000 ₽'],
                        ['Machine Learning',     '4 месяца', 'Онлайн', '65 000 ₽'],
                    ],
                },
            },
            {
                'type': 'faq', 'title': 'Частые вопросы', 'order': 3,
                'data': {
                    'icon_style': 'arrow',
                    'items': [
                        {'question': 'Нужен ли опыт программирования?',
                         'answer': '<p>Нет, большинство курсов рассчитаны на абсолютных новичков.</p>'},
                        {'question': 'Сколько времени нужно уделять учёбе?',
                         'answer': '<p>В среднем 10–15 часов в неделю. Расписание гибкое.</p>'},
                        {'question': 'Есть ли трудоустройство после курса?',
                         'answer': '<p>Да, помогаем с резюме и рекомендуем партнёрам-работодателям.</p>'},
                        {'question': 'Можно ли вернуть деньги?',
                         'answer': '<p>Да, в течение первых 7 дней обучения — полный возврат.</p>'},
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
                    'heading': 'Свяжитесь с нами',
                    'subheading': 'Готовы ответить на любые вопросы',
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
                        {'type': 'phone',   'label': 'Телефон',  'value': '+7 (495) 123-45-67', 'description': ''},
                        {'type': 'email',   'label': 'Email',    'value': 'hello@school-start.ru', 'description': ''},
                        {'type': 'address', 'label': 'Адрес',    'value': 'Москва, ул. Пушкина, 10, офис 301', 'description': ''},
                        {'type': 'hours',   'label': 'График',   'value': 'Пн–Пт 9:00–21:00, Сб 10:00–18:00', 'description': ''},
                        {'type': 'social',  'label': 'ВКонтакте','value': 'https://vk.com/school_start', 'description': ''},
                    ],
                },
            },
            {
                'type': 'form', 'title': 'Напишите нам', 'order': 2,
                'data': {
                    'description': 'Задайте вопрос — ответим быстро',
                    'button_text': 'Отправить',
                    'success_message': 'Спасибо! Ответим в течение часа.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',     'label': 'Имя',    'required': True},
                        {'name': 'field_2', 'type': 'email',    'label': 'Email',  'required': True},
                        {'name': 'field_3', 'type': 'textarea', 'label': 'Вопрос', 'required': True},
                    ],
                },
            },
        ],
    },
]

LEADS = [
    {'data': {'Ваше имя': 'Мария Иванова', 'Телефон': '+7 916 111-22-33', 'Какой курс интересует?': 'Python'}},
    {'data': {'Ваше имя': 'Алексей Петров', 'Телефон': '+7 903 444-55-66', 'Какой курс интересует?': 'Frontend'}},
]


class Command(BaseCommand):
    help = 'Заполняет базу данными онлайн-школы «Старт»'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить базу перед заполнением')

    def handle(self, *args, **options):
        if options['clear']:
            from django.core.management import call_command
            call_command('clear_db', '--yes', '--keep-users')

        self.stdout.write(self.style.HTTP_INFO('\n🌱  Заполняем базу — Онлайн-школа «Старт»\n'))
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
        s.site_name = 'Школа Старт'; s.nav_mode = 'name_only'
        s.contact_phone = '+7 (495) 123-45-67'; s.contact_email = 'hello@school-start.ru'
        s.contact_address = 'Москва, ул. Пушкина, 10'; s.contact_hours = 'Пн–Пт 9:00–21:00'
        theme = Theme.objects.first()
        if theme: s.active_theme = theme
        s.save()
        self.stdout.write(f'   ✅ {s.site_name}')