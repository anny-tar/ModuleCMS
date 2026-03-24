"""
Команда: python manage.py seed_db

Заполняет базу данных демо-данными для онлайн-школы:
- Создаёт суперпользователя и двух сотрудников
- Создаёт страницы: Главная, О нас, Курсы, Новости, Галерея, Контакты
- Заполняет страницы секциями
- Создаёт категории и статьи новостей
- Создаёт тестовые заявки
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


# ── Демо-данные ──────────────────────────────────────────────────────────────

USERS = [
    {
        'username':   'admin',
        'password':   'admin123',
        'email':      'admin@school.ru',
        'first_name': 'Администратор',
        'last_name':  '',
        'is_superuser': True,
        'is_staff':   True,
        'role':       'Суперпользователь',
    },
    {
        'username':   'manager',
        'password':   'manager123',
        'email':      'manager@school.ru',
        'first_name': 'Анна',
        'last_name':  'Петрова',
        'is_superuser': False,
        'is_staff':   True,
        'role':       'Менеджер контента',
    },
    {
        'username':   'editor',
        'password':   'editor123',
        'email':      'editor@school.ru',
        'first_name': 'Иван',
        'last_name':  'Сидоров',
        'is_superuser': False,
        'is_staff':   True,
        'role':       'Редактор',
    },
]

NEWS_CATEGORIES = ['Новости школы', 'Анонсы курсов', 'Истории успеха', 'Советы и статьи']

ARTICLES = [
    {
        'title':      'Открытие нового курса по Python',
        'category':   'Анонсы курсов',
        'announce':   'С 1 февраля стартует интенсивный курс по Python для начинающих.',
        'content':    '<p>Мы рады сообщить об открытии нового курса <strong>Python с нуля</strong>. '
                      'Программа рассчитана на 3 месяца и включает 48 практических занятий.</p>'
                      '<p>Вас ждут: основы языка, работа с данными, создание веб-приложений и финальный проект.</p>',
        'is_published': True,
    },
    {
        'title':      'Наши выпускники устроились в Яндекс и Сбер',
        'category':   'Истории успеха',
        'announce':   '15 выпускников нашей школы получили офферы от ведущих IT-компаний.',
        'content':    '<p>Мы гордимся нашими студентами! В этом квартале сразу 15 выпускников '
                      'получили предложения о работе от крупнейших технологических компаний.</p>'
                      '<p>Средняя зарплата наших выпускников составляет 120 000 рублей в месяц.</p>',
        'is_published': True,
    },
    {
        'title':      'Как выбрать первый язык программирования',
        'category':   'Советы и статьи',
        'announce':   'Разбираем плюсы и минусы популярных языков для начинающих.',
        'content':    '<p>Один из самых частых вопросов от новичков — с чего начать? '
                      'В этой статье мы сравниваем Python, JavaScript и Java.</p>'
                      '<p><strong>Python</strong> — лучший выбор для большинства новичков благодаря '
                      'простому синтаксису и широкому применению.</p>',
        'is_published': True,
    },
    {
        'title':      'День открытых дверей — 15 марта',
        'category':   'Новости школы',
        'announce':   'Приглашаем всех желающих на бесплатное мероприятие.',
        'content':    '<p>15 марта в 18:00 состоится день открытых дверей онлайн-школы Старт.</p>'
                      '<p>Вы сможете познакомиться с преподавателями, задать вопросы и получить '
                      'скидку 20% на любой курс при записи в день мероприятия.</p>',
        'is_published': True,
    },
    {
        'title':      'Новый формат обучения: воркшопы по пятницам',
        'category':   'Новости школы',
        'announce':   'Каждую пятницу — бесплатные практические занятия для студентов.',
        'content':    '<p>С этого месяца мы запускаем еженедельные воркшопы по пятницам в 19:00.</p>'
                      '<p>Темы: разбор реальных задач с собеседований, code review, работа в команде.</p>',
        'is_published': False,
    },
]

PAGES = [
    {
        'title':     'Главная',
        'slug':      'glavnaia',
        'page_type': 'default',
        'order':     0,
        'sections':  [
            {
                'type':  'hero',
                'title': '',
                'order': 0,
                'data':  {
                    'heading':    'Освойте IT-профессию за 3–6 месяцев',
                    'subheading': 'Практическое обучение от действующих специалистов. '
                                  'Помогаем найти первую работу.',
                    'align':      'left',
                    'buttons':    'two',
                    'btn1_text':  'Выбрать курс',
                    'btn1_url':   '/kursy/',
                    'btn2_text':  'Узнать подробнее',
                    'btn2_url':   '/o-nas/',
                    'bg_mode':    'none',
                    'image_id':   None,
                },
            },
            {
                'type':  'counters',
                'title': 'Наши результаты',
                'order': 1,
                'data':  {
                    'items': [
                        {'value': '1200+', 'label': 'Выпускников'},
                        {'value': '87%',   'label': 'Трудоустроились'},
                        {'value': '18',    'label': 'Преподавателей'},
                        {'value': '4.9',   'label': 'Средняя оценка'},
                    ],
                },
            },
            {
                'type':  'cards',
                'title': 'Почему выбирают нас',
                'order': 2,
                'data':  {
                    'items': [
                        {'icon': '🎯', 'title': 'Практика с первого дня',
                         'text': '<p>Никакой теории ради теории. Сразу пишем код и делаем проекты.</p>'},
                        {'icon': '👨‍💼', 'title': 'Преподаватели-практики',
                         'text': '<p>Все наши преподаватели работают в IT-компаниях прямо сейчас.</p>'},
                        {'icon': '💼', 'title': 'Помощь с трудоустройством',
                         'text': '<p>Помогаем составить резюме и готовим к техническим собеседованиям.</p>'},
                    ],
                },
            },
            {
                'type':  'steps',
                'title': 'Как проходит обучение',
                'order': 3,
                'data':  {
                    'direction': 'horizontal',
                    'items': [
                        {'icon': '1️⃣', 'title': 'Выбираете курс',
                         'description': '<p>Консультируемся и подбираем подходящую программу.</p>'},
                        {'icon': '2️⃣', 'title': 'Учитесь онлайн',
                         'description': '<p>Видеоуроки, практика, проверка домашних заданий.</p>'},
                        {'icon': '3️⃣', 'title': 'Делаете проект',
                         'description': '<p>Финальный проект для портфолио с обратной связью.</p>'},
                        {'icon': '4️⃣', 'title': 'Находите работу',
                         'description': '<p>Помогаем с резюме и готовим к собеседованиям.</p>'},
                    ],
                },
            },
            {
                'type':  'testimonials',
                'title': 'Отзывы студентов',
                'order': 4,
                'data':  {
                    'items': [
                        {'name': 'Мария К.', 'role': 'Frontend-разработчик в Сбере',
                         'text': '<p>За 4 месяца с нуля до первой работы. Преподаватели всегда на связи, '
                                 'объясняют понятно. Очень довольна!</p>',
                         'photo_id': None},
                        {'name': 'Алексей Т.', 'role': 'Python-разработчик',
                         'text': '<p>Курс помог структурировать знания и найти работу на 40% выше '
                                 'предыдущей зарплаты. Рекомендую всем!</p>',
                         'photo_id': None},
                        {'name': 'Светлана Н.', 'role': 'Data Analyst',
                         'text': '<p>Хотела сменить профессию — получилось! Теперь работаю аналитиком '
                                 'данных в e-commerce компании.</p>',
                         'photo_id': None},
                    ],
                },
            },
            {
                'type':  'form',
                'title': 'Запишитесь на бесплатную консультацию',
                'order': 5,
                'data':  {
                    'description':     'Ответим на все вопросы и поможем выбрать подходящий курс',
                    'button_text':     'Отправить заявку',
                    'success_message': 'Спасибо! Мы свяжемся с вами в течение часа.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',  'label': 'Ваше имя',    'required': True},
                        {'name': 'field_2', 'type': 'tel',   'label': 'Телефон',     'required': True},
                        {'name': 'field_3', 'type': 'email', 'label': 'Email',       'required': False},
                        {'name': 'field_4', 'type': 'text',  'label': 'Какой курс интересует?', 'required': False},
                    ],
                },
            },
        ],
    },
    {
        'title':     'О нас',
        'slug':      'o-nas',
        'page_type': 'default',
        'order':     1,
        'sections':  [
            {
                'type':  'hero',
                'title': '',
                'order': 0,
                'data':  {
                    'heading':    'О школе Старт',
                    'subheading': 'Мы помогаем людям войти в IT с 2018 года',
                    'align':      'center',
                    'buttons':    'none',
                    'bg_mode':    'none',
                    'image_id':   None,
                },
            },
            {
                'type':  'text',
                'title': 'Наша история',
                'order': 1,
                'data':  {
                    'content': '<p>Школа Старт основана в 2018 году практикующими специалистами из IT и '
                               'маркетинга. Мы устали от теоретических курсов, после которых непонятно '
                               'что делать — и создали школу, где обучение строится вокруг реальных задач.</p>'
                               '<p>Каждый <strong>курс</strong> — это не лекции, а работа над проектами. '
                               'Уже в процессе обучения студенты создают портфолио, которое можно показать '
                               'работодателю.</p>'
                               '<p>Наши выпускники устраиваются на работу в среднем через 2 месяца после '
                               'окончания курса.</p>',
                },
            },
            {
                'type':  'team',
                'title': 'Наши преподаватели',
                'order': 2,
                'data':  {
                    'items': [
                        {'name': 'Дмитрий Волков', 'position': 'Python, Backend',
                         'description': '<p>10 лет в разработке. Работал в Яндексе и Mail.ru.</p>',
                         'photo_id': None},
                        {'name': 'Екатерина Смирнова', 'position': 'Frontend, React',
                         'description': '<p>Senior Frontend в Тинькофф. Ведёт курсы 4 года.</p>',
                         'photo_id': None},
                        {'name': 'Артём Козлов', 'position': 'Data Science, ML',
                         'description': '<p>PhD в математике, DS в Сбере. Специалист по ML.</p>',
                         'photo_id': None},
                        {'name': 'Ольга Новикова', 'position': 'UX/UI Design',
                         'description': '<p>Дизайнер с 8-летним стажем. Работала в Авито.</p>',
                         'photo_id': None},
                    ],
                },
            },
        ],
    },
    {
        'title':     'Курсы',
        'slug':      'kursy',
        'page_type': 'default',
        'order':     2,
        'sections':  [
            {
                'type':  'hero',
                'title': '',
                'order': 0,
                'data':  {
                    'heading':    'Наши курсы',
                    'subheading': 'Выберите направление и начните обучение уже сегодня',
                    'align':      'center',
                    'buttons':    'none',
                    'bg_mode':    'none',
                    'image_id':   None,
                },
            },
            {
                'type':  'cards',
                'title': 'Направления обучения',
                'order': 1,
                'data':  {
                    'items': [
                        {'icon': '🐍', 'title': 'Python-разработчик',
                         'text': '<p>3 месяца • от 0 до Junior</p><p>Backend, Django, REST API, PostgreSQL</p>'},
                        {'icon': '⚛️', 'title': 'Frontend-разработчик',
                         'text': '<p>4 месяца • от 0 до Junior</p><p>HTML, CSS, JavaScript, React</p>'},
                        {'icon': '📊', 'title': 'Data Analyst',
                         'text': '<p>3 месяца • от 0 до Junior</p><p>Python, SQL, Pandas, визуализация</p>'},
                        {'icon': '🎨', 'title': 'UX/UI дизайнер',
                         'text': '<p>2 месяца • от 0 до Junior</p><p>Figma, прототипы, юзабилити</p>'},
                        {'icon': '🤖', 'title': 'Machine Learning',
                         'text': '<p>4 месяца • уровень Middle</p><p>scikit-learn, TensorFlow, нейросети</p>'},
                        {'icon': '🔐', 'title': 'Кибербезопасность',
                         'text': '<p>3 месяца • от 0 до Junior</p><p>Основы ИБ, пентест, OWASP</p>'},
                    ],
                },
            },
            {
                'type':  'table',
                'title': 'Сравнение курсов',
                'order': 2,
                'data':  {
                    'style':   'zebra',
                    'headers': ['Курс', 'Длительность', 'Формат', 'Цена'],
                    'rows': [
                        ['Python-разработчик',  '3 месяца', 'Онлайн', '45 000 ₽'],
                        ['Frontend-разработчик', '4 месяца', 'Онлайн', '55 000 ₽'],
                        ['Data Analyst',         '3 месяца', 'Онлайн', '40 000 ₽'],
                        ['UX/UI дизайнер',       '2 месяца', 'Онлайн', '35 000 ₽'],
                        ['Machine Learning',     '4 месяца', 'Онлайн', '65 000 ₽'],
                    ],
                },
            },
            {
                'type':  'faq',
                'title': 'Частые вопросы',
                'order': 3,
                'data':  {
                    'icon_style': 'arrow',
                    'items': [
                        {'question': 'Нужен ли опыт программирования?',
                         'answer': '<p>Нет, большинство наших курсов рассчитаны на абсолютных новичков. '
                                   'Мы начинаем с самых основ.</p>'},
                        {'question': 'Сколько времени нужно уделять учёбе?',
                         'answer': '<p>В среднем 10–15 часов в неделю. Расписание гибкое — '
                                   'учитесь в удобное для вас время.</p>'},
                        {'question': 'Есть ли трудоустройство после курса?',
                         'answer': '<p>Да, мы помогаем с резюме, готовим к собеседованиям и '
                                   'рекомендуем выпускников нашим партнёрам-работодателям.</p>'},
                        {'question': 'Можно ли вернуть деньги?',
                         'answer': '<p>Да, в течение первых 7 дней обучения мы возвращаем '
                                   'полную стоимость без вопросов.</p>'},
                    ],
                },
            },
        ],
    },
    {
        'title':     'Новости',
        'slug':      'novosti',
        'page_type': 'news_list',
        'order':     3,
    },
    {
        'title':     'Галерея',
        'slug':      'galereya',
        'page_type': 'gallery',
        'order':     4,
    },
    {
        'title':     'Контакты',
        'slug':      'kontakty',
        'page_type': 'default',
        'order':     5,
        'sections':  [
            {
                'type':  'hero',
                'title': '',
                'order': 0,
                'data':  {
                    'heading':    'Свяжитесь с нами',
                    'subheading': 'Готовы ответить на любые вопросы',
                    'align':      'center',
                    'buttons':    'none',
                    'bg_mode':    'none',
                    'image_id':   None,
                },
            },
            {
                'type':  'contacts',
                'title': 'Наши контакты',
                'order': 1,
                'data':  {
                    'layout': 'none',
                    'map_url': '',
                    'map_label': '',
                    'map_description': '',
                    'items': [
                        {'type': 'address', 'label': 'Офис',     'value': 'Москва, ул. Пушкина, 10, офис 301', 'description': 'Пн–Пт 10:00–19:00'},
                        {'type': 'phone',   'label': 'Телефон',  'value': '+7 (495) 123-45-67', 'description': 'Звонить с 9:00 до 21:00'},
                        {'type': 'phone',   'label': 'WhatsApp', 'value': '+7 (916) 987-65-43', 'description': ''},
                        {'type': 'email',   'label': 'Email',    'value': 'hello@school-start.ru', 'description': 'Отвечаем в течение часа'},
                        {'type': 'social',  'label': 'ВКонтакте','value': 'https://vk.com/school_start', 'description': ''},
                        {'type': 'hours',   'label': 'График',   'value': 'Пн–Пт 9:00–21:00, Сб 10:00–18:00', 'description': ''},
                    ],
                },
            },
            {
                'type':  'form',
                'title': 'Напишите нам',
                'order': 2,
                'data':  {
                    'description':     'Задайте вопрос или оставьте заявку — ответим быстро',
                    'button_text':     'Отправить',
                    'success_message': 'Сообщение отправлено! Ответим в течение часа.',
                    'fields': [
                        {'name': 'field_1', 'type': 'text',     'label': 'Имя',     'required': True},
                        {'name': 'field_2', 'type': 'email',    'label': 'Email',   'required': True},
                        {'name': 'field_3', 'type': 'textarea', 'label': 'Вопрос',  'required': True},
                    ],
                },
            },
        ],
    },
]

LEADS = [
    {'section_title': 'Запись на консультацию',
     'data': {'Ваше имя': 'Мария Иванова', 'Телефон': '+7 916 123-45-67',
              'Email': 'maria@gmail.com', 'Какой курс интересует?': 'Python'}},
    {'section_title': 'Запись на консультацию',
     'data': {'Ваше имя': 'Алексей Петров', 'Телефон': '+7 903 987-65-43',
              'Email': '', 'Какой курс интересует?': 'Frontend'}},
    {'section_title': 'Запись на консультацию',
     'data': {'Ваше имя': 'Светлана Козлова', 'Телефон': '+7 926 555-44-33',
              'Email': 'sveta@mail.ru', 'Какой курс интересует?': 'Data Science'}},
]


class Command(BaseCommand):
    help = 'Заполняет базу данных демо-данными для онлайн-школы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу перед заполнением',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑  Очищаем базу перед заполнением...'))
            from django.core.management import call_command
            call_command('clear_db', '--yes', '--keep-users')

        self.stdout.write('\n' + '─' * 60)
        self.stdout.write(self.style.HTTP_INFO('🌱  Заполняем базу демо-данными (онлайн-школа)...'))
        self.stdout.write('─' * 60)

        with transaction.atomic():
            self._create_users()
            self._create_pages()
            self._create_news()
            self._create_leads()
            self._setup_site_settings()

        self.stdout.write('─' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅  База данных успешно заполнена!\n'))
        self.stdout.write('   Откройте http://127.0.0.1:8000/ для просмотра сайта')
        self.stdout.write('   Откройте http://127.0.0.1:8000/admin/ для входа в панель\n')

    # ── Пользователи ─────────────────────────────────────────────────────────

    def _create_users(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        self.stdout.write('\n👤  Пользователи:')
        self.stdout.write('   ' + '─' * 55)
        self.stdout.write(f'   {"Роль":<25} {"Логин":<15} {"Пароль":<15}')
        self.stdout.write('   ' + '─' * 55)

        for u in USERS:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email        = u['email']
            user.first_name   = u['first_name']
            user.last_name    = u['last_name']
            user.is_superuser = u['is_superuser']
            user.is_staff     = u['is_staff']
            user.set_password(u['password'])
            user.save()

            status = '✨ создан' if created else '🔄 обновлён'
            self.stdout.write(
                f'   {u["role"]:<25} {u["username"]:<15} {u["password"]:<15}  {status}'
            )

        self.stdout.write('   ' + '─' * 55)

    # ── Страницы и секции ────────────────────────────────────────────────────

    def _create_pages(self):
        from pages.models import Page, Section

        self.stdout.write('\n📄  Страницы и секции:')

        for p_data in PAGES:
            page, created = Page.objects.get_or_create(slug=p_data['slug'])
            page.title        = p_data['title']
            page.page_type    = p_data['page_type']
            page.order        = p_data['order']
            page.is_published = True
            page.save()

            sections = p_data.get('sections', [])
            # Удаляем старые секции этой страницы
            Section.objects.filter(page=page).delete()

            for s_data in sections:
                Section.objects.create(
                    page       = page,
                    type       = s_data['type'],
                    title      = s_data.get('title', ''),
                    order      = s_data['order'],
                    is_visible = True,
                    data       = s_data.get('data', {}),
                )

            status = '✨' if created else '🔄'
            self.stdout.write(
                f'   {status} {page.title:<20} ({page.page_type}) — {len(sections)} секций'
            )

    # ── Новости ──────────────────────────────────────────────────────────────

    def _create_news(self):
        from news.models import Category, Article

        self.stdout.write('\n📰  Новости:')

        cats = {}
        for name in NEWS_CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name)
            cats[name] = cat

        for a_data in ARTICLES:
            article, created = Article.objects.get_or_create(title=a_data['title'])
            article.category     = cats.get(a_data['category'])
            article.announce     = a_data['announce']
            article.content      = a_data['content']
            article.is_published = a_data['is_published']
            article.published_at = timezone.now()
            article.save()

            status = '✨' if created else '🔄'
            pub = '✅' if article.is_published else '📝'
            self.stdout.write(f'   {status} {pub} {article.title[:50]}')

    # ── Заявки ───────────────────────────────────────────────────────────────

    def _create_leads(self):
        from leads.models import LeadSubmission

        self.stdout.write('\n📬  Тестовые заявки:')

        for lead in LEADS:
            obj = LeadSubmission.objects.create(
                section_id = 1,
                data       = lead['data'],
                ip_address = f'192.168.1.{random.randint(1, 254)}',
            )
            name = lead['data'].get('Ваше имя', '—')
            self.stdout.write(f'   ✨ Заявка от {name}')

    # ── Настройки сайта ──────────────────────────────────────────────────────

    def _setup_site_settings(self):
        from appearance.models import SiteSettings, Theme

        self.stdout.write('\n⚙️  Настройки сайта:')

        settings = SiteSettings.get()
        settings.site_name      = 'Школа Старт'
        settings.nav_mode       = 'name_only'
        settings.contact_phone  = '+7 (495) 123-45-67'
        settings.contact_email  = 'hello@school-start.ru'
        settings.contact_address = 'Москва, ул. Пушкина, 10'
        settings.contact_hours  = 'Пн–Пт 9:00–21:00'

        # Ставим первую тему по умолчанию
        theme = Theme.objects.first()
        if theme:
            settings.active_theme = theme

        settings.save()
        self.stdout.write(f'   ✅ Название сайта: "{settings.site_name}"')
        self.stdout.write(f'   ✅ Тема оформления: "{theme.name if theme else "не выбрана"}"')