"""
Команда наполнения БД демо-данными школы курсов «Старт».

Использование:
    python manage.py seed_school
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Наполняет БД демо-данными школы курсов «Старт»'

    def handle(self, *args, **options):
        from pages.management.commands.seed_base import clear_all, create_users, create_appearance

        self.stdout.write('Очистка БД...')
        clear_all()

        self.stdout.write('Создание пользователей...')
        create_users()

        self.stdout.write('Создание оформления...')
        theme, font = create_appearance(
            primary='#7c3aed', background='#ffffff', surface='#f5f3ff',
            accent='#6d28d9', text='#1e1b4b',
            font_name='Inter', font_google='Inter',
        )

        self.stdout.write('Создание настроек...')
        self._settings(theme, font)

        self.stdout.write('Создание страниц...')
        self._pages()

        self.stdout.write('Создание новостей...')
        self._news()

        self.stdout.write('Создание галереи...')
        self._gallery()

        self.stdout.write('Создание заявок...')
        self._leads()

        self.stdout.write(self.style.SUCCESS(
            '\nШкола «Старт» готова. http://127.0.0.1:8000/\n'
            'admin / admin1234\n'
            'director / director1234\n'
            'manager / manager1234\n'
            'editor / editor1234'
        ))

    def _settings(self, theme, font):
        from appearance.models import SiteSettings
        SiteSettings.objects.create(
            pk=1, site_name='Школа Старт',
            active_theme=theme, active_font=font,
            contact_address='г. Москва, ул. Арбат, д. 24, офис 301',
            contact_phone='+7 (495) 456-78-90',
            contact_email='hello@shkola-start.ru',
            contact_hours='Пн–Пт: 9:00–20:00, Сб: 10:00–16:00',
        )

    def _pages(self):
        from pages.models import Page, Section, PageType

        home = Page.objects.create(
            title='Главная', slug='glavnaya', page_type=PageType.DEFAULT,
            is_published=True, order=0,
            seo_title='Школа Старт — онлайн и офлайн курсы в Москве',
        )
        o = 0

        Section.objects.create(page=home, type='hero', order=o, is_visible=True, data={
            'heading': 'Получите новую профессию за 3–6 месяцев',
            'subheading': 'Практические курсы с трудоустройством. Онлайн и офлайн форматы. Более 500 выпускников нашли работу по специальности.',
            'button_text': 'Выбрать курс',
            'button_url': '/kursy/',
        }); o += 1

        Section.objects.create(page=home, type='text', title='О школе Старт', order=o, is_visible=True, data={
            'content': 'Школа Старт основана в 2018 году практикующими специалистами из IT и маркетинга. Мы устали от теоретических курсов, после которых непонятно что делать — и создали школу, где обучение строится вокруг реальных задач.\n\nКаждый курс — это не лекции, а работа над проектами. Уже в процессе обучения студенты создают портфолио, которое можно показать работодателю. Наши выпускники устраиваются на работу в среднем через 2 месяца после окончания курса.\n\nСегодня в школе работают 18 преподавателей — действующих специалистов из Яндекса, Сбера, Mail.ru и других компаний. Мы не приглашаем теоретиков: все преподаватели практикуют то, чему учат.',
        }); o += 1

        Section.objects.create(page=home, type='counters', title='Школа в цифрах', order=o, is_visible=True, data={
            'items': [
                {'value': '500+', 'label': 'Выпускников'},
                {'value': '8',    'label': 'Направлений обучения'},
                {'value': '87%',  'label': 'Трудоустроились'},
                {'value': '6',    'label': 'Лет на рынке'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='cards', title='Почему выбирают нас', order=o, is_visible=True, data={
            'items': [
                {'icon': '💻', 'title': 'Практика с первого дня', 'text': 'Никакой «сухой» теории. С первого занятия работаете над реальными задачами и создаёте портфолио.'},
                {'icon': '👨‍💼', 'title': 'Преподаватели-практики', 'text': 'Все преподаватели — действующие специалисты из крупных компаний. Учат тому, что работает сейчас.'},
                {'icon': '🎯', 'title': 'Помощь с трудоустройством', 'text': '87% выпускников нашли работу по специальности. Помогаем с резюме, портфолио и подготовкой к собеседованиям.'},
                {'icon': '📱', 'title': 'Онлайн и офлайн', 'text': 'Выбирайте удобный формат. Онлайн — учитесь из любой точки мира. Офлайн — живое общение и нетворкинг.'},
                {'icon': '🔄', 'title': 'Актуальная программа', 'text': 'Программы обновляются каждые 6 месяцев. Учим только тем инструментам, которые востребованы работодателями.'},
                {'icon': '💳', 'title': 'Рассрочка без %', 'text': 'Оплата в рассрочку на 12 месяцев. Без банков и переплат — напрямую с школой.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='text', title='Как устроено обучение', order=o, is_visible=True, data={
            'content': 'Каждый курс разбит на модули по 2–3 недели. В конце каждого модуля — практическое задание, которое проверяет куратор и даёт подробную обратную связь.\n\nОнлайн-занятия проходят в прямом эфире 2–3 раза в неделю. Все занятия записываются и доступны в личном кабинете без ограничений по времени.\n\nДля офлайн-студентов — занятия в нашем учебном центре на Арбате. Небольшие группы по 8–12 человек, живое общение с преподавателем и одногруппниками.\n\nПо окончании курса выдаётся сертификат установленного образца. Помогаем составить резюме и портфолио, проводим мок-интервью и рекомендуем выпускников работодателям из нашей партнёрской сети.',
        }); o += 1

        Section.objects.create(page=home, type='steps', title='Путь от записи до работы', order=o, is_visible=True, data={
            'items': [
                {'title': 'Выбираете курс',        'description': 'Проходите бесплатную консультацию с методистом. Подбираем курс под ваши цели и уровень подготовки.'},
                {'title': 'Начинаете обучение',    'description': 'Первый модуль — бесплатный. Убеждаетесь, что формат подходит, затем оформляете оплату или рассрочку.'},
                {'title': 'Работаете над проектами','description': 'Каждый модуль — практическое задание. К концу курса у вас готовое портфолио из 5–7 реальных работ.'},
                {'title': 'Готовитесь к работе',   'description': 'Карьерный центр помогает с резюме, LinkedIn и подготовкой к собеседованиям. Проводим мок-интервью.'},
                {'title': 'Находите работу',        'description': 'Рекомендуем вас работодателям из партнёрской сети. Средний срок трудоустройства — 2 месяца после выпуска.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='testimonials', title='Истории выпускников', order=o, is_visible=True, data={
            'items': [
                {'name': 'Анна Кириллова, выпускница курса Python-разработчик', 'text': 'До школы работала бухгалтером. За 5 месяцев освоила Python и Django, собрала портфолио. Через 6 недель после выпуска вышла junior-разработчиком в IT-компанию с зарплатой вдвое выше предыдущей.'},
                {'name': 'Михаил Соловьёв, выпускник курса Интернет-маркетинг', 'text': 'Пришёл совсем без опыта. Преподаватели объясняли понятно, задания были реальными. На курсе вёл кампании в Яндекс.Директ для учебного клиента — это и стало первым кейсом в портфолио.'},
                {'name': 'Светлана Орлова, выпускница курса UX/UI дизайн',      'text': 'Рисовала для себя, хотела перейти в профессию. После курса собрала портфолио из 6 проектов. Сейчас работаю в агентстве и параллельно делаю фриланс.'},
                {'name': 'Денис Павлов, выпускник курса Data Science',           'text': 'Выбрал офлайн-формат — очень важно было живое общение. Группа маленькая, преподаватель всегда отвечал на вопросы. Это сильно ускорило обучение.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='faq', title='Часто задаваемые вопросы', order=o, is_visible=True, data={
            'items': [
                {'question': 'Нужны ли предварительные знания?',
                 'answer': 'Зависит от курса. Большинство курсов рассчитаны на новичков без технического опыта. Для продвинутых уровней — указано в описании курса. На бесплатной консультации методист поможет выбрать подходящий уровень.'},
                {'question': 'Можно ли совмещать с работой?',
                 'answer': 'Да. Занятия проходят вечером и на выходных. В онлайн-формате занятия записываются и доступны в любое время. Большинство наших студентов совмещают обучение с работой.'},
                {'question': 'Что если я отстану от группы?',
                 'answer': 'Все занятия записываются и доступны в личном кабинете без ограничений. Куратор помогает «догнать» пропущенные темы. При необходимости можно перейти в следующий поток бесплатно.'},
                {'question': 'Выдаёте ли вы документы об окончании?',
                 'answer': 'Да. По окончании курса выдаётся сертификат установленного образца. Для некоторых курсов доступно удостоверение о повышении квалификации государственного образца.'},
                {'question': 'Как работает рассрочка?',
                 'answer': 'Рассрочка на 12 месяцев без процентов — напрямую с школой, без банков. Первый платёж — при записи. Далее ежемесячно до полного погашения стоимости курса.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='form', title='Записаться на бесплатную консультацию', order=o, is_visible=True, data={
            'fields': [
                {'name': 'name',    'type': 'text',     'label': 'Ваше имя',      'required': True},
                {'name': 'phone',   'type': 'tel',      'label': 'Телефон',       'required': True},
                {'name': 'course',  'type': 'text',     'label': 'Интересный курс','required': False},
                {'name': 'format',  'type': 'text',     'label': 'Формат (онлайн/офлайн)', 'required': False},
                {'name': 'message', 'type': 'textarea', 'label': 'Вопрос',        'required': False},
            ]
        })

        # Страница "Курсы"
        courses_page = Page.objects.create(
            title='Курсы', slug='kursy', page_type=PageType.DEFAULT,
            is_published=True, order=1,
        )
        o = 0

        Section.objects.create(page=courses_page, type='text', title='Наши направления', order=o, is_visible=True, data={
            'content': 'Школа Старт предлагает курсы по восьми направлениям. Все программы разработаны совместно с работодателями и регулярно обновляются. Мы не учим устаревшим инструментам — только то, что востребовано на рынке труда сегодня.',
        }); o += 1

        Section.objects.create(page=courses_page, type='cards', title='Направления обучения', order=o, is_visible=True, data={
            'items': [
                {'icon': '🐍', 'title': 'Python-разработчик',  'text': '5 месяцев. Python, Django, PostgreSQL, REST API. От основ до полноценного бэкенда.'},
                {'icon': '🎨', 'title': 'UX/UI дизайн',        'text': '4 месяца. Figma, прототипирование, юзабилити. Портфолио из 6 реальных проектов.'},
                {'icon': '📊', 'title': 'Data Science',         'text': '6 месяцев. Python, pandas, ML. Анализ данных и машинное обучение с нуля.'},
                {'icon': '📱', 'title': 'Интернет-маркетинг',  'text': '3 месяца. Контекст, таргет, SEO, аналитика. Полный digital-маркетинг.'},
                {'icon': '🌐', 'title': 'Веб-разработка',      'text': '4 месяца. HTML, CSS, JavaScript, React. Фронтенд с нуля до трудоустройства.'},
                {'icon': '📋', 'title': 'Управление проектами', 'text': '3 месяца. Agile, Scrum, Jira. Подготовка к сертификации PMP.'},
                {'icon': '🔐', 'title': 'Кибербезопасность',   'text': '5 месяцев. Пентест, сетевая безопасность, OSINT. Практика на реальных стендах.'},
                {'icon': '☁️', 'title': 'Облачные технологии', 'text': '4 месяца. AWS, Docker, Kubernetes. Подготовка к сертификации AWS Solutions Architect.'},
            ]
        }); o += 1

        Section.objects.create(page=courses_page, type='table', title='Сравнение форматов', order=o, is_visible=True, data={
            'headers': ['Параметр', 'Онлайн', 'Офлайн'],
            'rows': [
                ['Место занятий',       'Из любой точки мира', 'Учебный центр, Арбат'],
                ['Размер группы',       'До 25 человек',       'До 12 человек'],
                ['Занятия в записи',    'Да, без ограничений', 'Да, без ограничений'],
                ['Живое общение',       'В чате и на Q&A',     'На каждом занятии'],
                ['Нетворкинг',          'В онлайн-сообществе', 'С одногруппниками лично'],
                ['Стоимость',           'От 35 000 ₽',         'От 55 000 ₽'],
            ]
        }); o += 1

        Section.objects.create(page=courses_page, type='text', title='Как построена программа', order=o, is_visible=True, data={
            'content': 'Каждый курс состоит из модулей по 2–3 недели. Внутри каждого модуля — видеолекции, практические задания и живые сессии с преподавателем.\n\nПрактические задания — это не учебные упражнения, а реальные задачи. Например, на курсе Python студенты разрабатывают API для реального небольшого бизнеса. На курсе UX/UI — проектируют интерфейс под реального клиента.\n\nВ конце курса — дипломный проект. Это полноценная работа, которую можно добавить в портфолио. Лучшие дипломные проекты публикуются на сайте школы.',
        }); o += 1

        Section.objects.create(page=courses_page, type='chart_pie', title='Наши выпускники работают в', order=o, is_visible=True, data={
            'title': 'Распределение по отраслям',
            'items': [
                {'label': 'IT-компании',        'value': '42'},
                {'label': 'Digital-агентства',  'value': '23'},
                {'label': 'Банки и финтех',     'value': '15'},
                {'label': 'Ритейл и e-commerce','value': '12'},
                {'label': 'Фриланс',            'value': '8'},
            ]
        }); o += 1

        Section.objects.create(page=courses_page, type='form', title='Не знаете какой курс выбрать?', order=o, is_visible=True, data={
            'fields': [
                {'name': 'name',  'type': 'text', 'label': 'Ваше имя', 'required': True},
                {'name': 'phone', 'type': 'tel',  'label': 'Телефон',  'required': True},
                {'name': 'goal',  'type': 'text', 'label': 'Ваша цель (хочу стать...)', 'required': False},
            ]
        })

        # Страница "Преподаватели"
        teachers_page = Page.objects.create(
            title='Преподаватели', slug='prepodavateli', page_type=PageType.DEFAULT,
            is_published=True, order=2,
        )
        o = 0

        Section.objects.create(page=teachers_page, type='text', title='Люди, которые учат', order=o, is_visible=True, data={
            'content': 'В Школе Старт нет преподавателей, которые занимаются только преподаванием. Каждый из них — практикующий специалист, который каждый день решает задачи по своей специальности.\n\nМы принципиально не приглашаем людей, которые давно ушли из практики. Рынок меняется быстро, и только тот, кто работает «в поле», знает что актуально сегодня и что будет востребовано завтра.',
        }); o += 1

        Section.objects.create(page=teachers_page, type='team', title='Наша команда', order=o, is_visible=True, data={
            'items': [
                {'name': 'Алексей Громов',   'position': 'Python, Django, архитектура',     'description': 'Senior Backend Developer в Яндексе. 12 лет в разработке. Автор двух open-source библиотек.'},
                {'name': 'Екатерина Орлова', 'position': 'UX/UI дизайн, Figma',             'description': 'Product Designer в Mail.ru. 8 лет в дизайне интерфейсов. Работала над интерфейсами с аудиторией 10+ млн.'},
                {'name': 'Виктор Лебедев',   'position': 'Data Science, ML',                'description': 'Lead Data Scientist в Сбере. PhD по математике. Автор курса на Coursera с 5 000+ слушателей.'},
                {'name': 'Наталья Чернова',  'position': 'Интернет-маркетинг, аналитика',   'description': 'Head of Performance Marketing в e-commerce компании. Управляет бюджетами 50+ млн ₽/мес.'},
                {'name': 'Роман Козырев',    'position': 'Веб-разработка, React',            'description': 'Frontend Lead в финтех-стартапе. 10 лет в фронтенде. Спикер конференций HolyJS и FrontendConf.'},
                {'name': 'Диана Морозова',   'position': 'Управление проектами, Agile',     'description': 'Project Director в консалтинговой компании. PMP, PMI-ACP. Реализовала 40+ проектов.'},
            ]
        }); o += 1

        Section.objects.create(page=teachers_page, type='counters', title='Команда преподавателей', order=o, is_visible=True, data={
            'items': [
                {'value': '18', 'label': 'Преподавателей'},
                {'value': '10+','label': 'Лет средний опыт'},
                {'value': '6',  'label': 'Компаний из топ-100'},
                {'value': '3',  'label': 'Спикера крупных конференций'},
            ]
        }); o += 1

        Section.objects.create(page=teachers_page, type='text', title='Как мы отбираем преподавателей', order=o, is_visible=True, data={
            'content': 'Отбор преподавателей — многоэтапный процесс. Сначала изучаем портфолио и опыт. Затем проводим техническое собеседование с действующими специалистами — проверяем актуальность знаний.\n\nДалее кандидат проводит пробное занятие: смотрим как объясняет, как отвечает на вопросы, умеет ли давать полезную обратную связь.\n\nИз 10 кандидатов проходят 2–3. Это высокий фильтр, который обеспечивает качество обучения.',
        }); o += 1

        Section.objects.create(page=teachers_page, type='form', title='Хотите преподавать у нас?', order=o, is_visible=True, data={
            'fields': [
                {'name': 'name',       'type': 'text',     'label': 'Ваше имя',         'required': True},
                {'name': 'phone',      'type': 'tel',      'label': 'Телефон',          'required': True},
                {'name': 'speciality', 'type': 'text',     'label': 'Специализация',    'required': True},
                {'name': 'experience', 'type': 'text',     'label': 'Опыт работы',      'required': False},
                {'name': 'message',    'type': 'textarea', 'label': 'О себе кратко',    'required': False},
            ]
        })

        Page.objects.create(title='Новости', slug='novosti', page_type=PageType.NEWS, is_published=True, order=3)
        Page.objects.create(title='Галерея', slug='galereya', page_type=PageType.GALLERY, is_published=True, order=4)
        Page.objects.create(title='Контакты', slug='kontakty', page_type=PageType.CONTACTS, is_published=True, order=5)

    def _news(self):
        from news.models import Category, Article
        cat_school    = Category.objects.create(name='Новости школы',    order=0)
        cat_graduates = Category.objects.create(name='Истории успеха',   order=1)
        cat_tips      = Category.objects.create(name='Советы и статьи',  order=2)

        Article.objects.create(
            title='Запускаем новый курс по кибербезопасности',
            slug='novyj-kurs-kiberbezopasnost',
            category=cat_school, is_published=True,
            published_at=timezone.now().replace(month=2, day=5),
            announce='С марта 2025 года открываем набор на курс «Специалист по кибербезопасности». 5 месяцев, практика на реальных стендах.',
            content='Школа Старт запускает новый курс «Специалист по кибербезопасности». Старт — 1 марта 2025 года.\n\nПрограмма рассчитана на 5 месяцев. Курс охватывает: основы сетевой безопасности, пентест веб-приложений, OSINT, защита инфраструктуры, работа с SIEM-системами.\n\nПреподаватель — Антон Волков, 10 лет в информационной безопасности, сертифицирован CEH и OSCP.\n\nЗанятия проходят на специально настроенных стендах — учебная среда максимально приближена к реальной. По окончании выдаётся сертификат. Помогаем с трудоустройством в SOC и информационную безопасность.',
        )
        Article.objects.create(
            title='Анна стала Python-разработчиком за 5 месяцев',
            slug='anna-python-razrabotchik',
            category=cat_graduates, is_published=True,
            published_at=timezone.now().replace(month=1, day=20),
            announce='История выпускницы, которая пришла бухгалтером и вышла junior-разработчиком с зарплатой вдвое выше.',
            content='Анне Кирилловой было 28 лет, когда она решила сменить профессию. Работала бухгалтером в небольшой компании и давно думала об IT — казалось перспективнее и интереснее.\n\n«Я пробовала самостоятельно учиться по YouTube, но без структуры и обратной связи прогресса не было. Нужна была система», — рассказывает Анна.\n\nОна выбрала курс Python-разработчик в Школе Старт и занималась вечерами, совмещая с работой. Самым сложным оказался третий месяц — когда надо было разобраться с базами данных и API.\n\nЧерез 5 месяцев Анна защитила дипломный проект — REST API для системы учёта заявок. Куратор помог оформить резюме и GitHub. Через 6 недель после выпуска Анна вышла на работу junior Python-разработчиком с зарплатой 85 000 ₽ — вдвое больше, чем на предыдущем месте.',
        )
        Article.objects.create(
            title='Как составить резюме без опыта работы',
            slug='rezyume-bez-opyta',
            category=cat_tips, is_published=True,
            published_at=timezone.now().replace(month=1, day=12),
            announce='Советы карьерного центра школы: как правильно составить первое резюме после курса.',
            content='Отсутствие коммерческого опыта — не приговор. Многие выпускники наших курсов успешно трудоустраиваются именно потому, что правильно подают то, что есть.\n\nУкажите учебные проекты. Если вы разработали 3–4 проекта на курсе — опишите их как опыт. Укажите технологии, задачи, результат. Ссылка на GitHub обязательна.\n\nНе пишите «без опыта». Пишите «опыт в учебных проектах 5 месяцев». Это честно и звучит лучше.\n\nОпишите смежный опыт. Работали менеджером? Это плюс для позиции project manager или аналитика. Были бухгалтером? Это ценно для финтех-компаний.\n\nСопроводительное письмо работает. 80% кандидатов его не пишут. Напишите 3–4 предложения: почему эта компания и почему вы готовы вложиться.',
        )
        Article.objects.create(
            title='5 инструментов Python-разработчика которые нужно знать в 2025',
            slug='5-instrumentov-python-2025',
            category=cat_tips, is_published=True,
            published_at=timezone.now().replace(month=3, day=10),
            announce='Преподаватель курса Python рассказывает о самых востребованных инструментах в 2025 году.',
            content='Рынок Python-разработки продолжает расти. В 2025 году работодатели ожидают знания этих инструментов уже у junior-разработчиков.\n\nFastAPI. Фреймворк для создания REST API. Быстрее Django REST Framework в продакшене, удобнее Flask для больших проектов. Стал стандартом во многих компаниях.\n\nPydantic v2. Валидация данных. Работает значительно быстрее первой версии. Используется в FastAPI и самостоятельно.\n\nDocker. Контейнеризация. Без Docker сложно попасть даже на junior-позицию. Умение написать Dockerfile и docker-compose — обязательно.\n\nPostgreSQL + asyncpg. Асинхронная работа с базами данных всё популярнее. asyncpg — самая быстрая библиотека для PostgreSQL в Python.\n\nGit и GitHub Actions. Системы контроля версий знают все. Но CI/CD через GitHub Actions — то, что отличает сильного junior от слабого.',
        )

    def _gallery(self):
        from gallery.models import Album
        Album.objects.create(title='Учебный центр на Арбате',   description='Аудитории, оборудование, пространство для общения.', order=0, is_published=True)
        Album.objects.create(title='Занятия и воркшопы',        description='Офлайн-занятия, мастер-классы, демо-дни.',            order=1, is_published=True)
        Album.objects.create(title='Выпускные церемонии',       description='Вручение сертификатов выпускникам потоков.',           order=2, is_published=True)
        Album.objects.create(title='Корпоративное обучение',    description='Программы для команд компаний.',                      order=3, is_published=True)

    def _leads(self):
        from leads.models import LeadSubmission
        for l in [
            {'data': {'name': 'Антон Власов',    'phone': '+7 (916) 222-33-44', 'course': 'Python-разработчик', 'format': 'Онлайн',  'message': 'Хочу сменить профессию с нуля'}, 'is_viewed': False},
            {'data': {'name': 'Юлия Степанова',  'phone': '+7 (903) 555-66-77', 'course': 'UX/UI дизайн',       'format': 'Офлайн', 'message': 'Уже рисую, хочу в профессию'},   'is_viewed': True},
            {'data': {'name': 'Кирилл Медведев', 'phone': '+7 (925) 888-99-00', 'course': 'Data Science',        'format': 'Онлайн',  'message': 'Есть матбаза, нужен практикум'}, 'is_viewed': False},
            {'data': {'name': 'Ольга Фёдорова',  'phone': '+7 (499) 111-00-22', 'course': 'Не знаю',            'format': 'Онлайн',  'message': 'Хочу в IT, не знаю с чего начать'}, 'is_viewed': True},
            {'data': {'name': 'Максим Рябов',    'phone': '+7 (926) 444-55-11', 'course': 'Кибербезопасность',  'format': 'Офлайн', 'message': 'Работаю сисадмином, хочу в безопасность'}, 'is_viewed': False},
        ]:
            LeadSubmission.objects.create(section_id=1, data=l['data'], is_viewed=l['is_viewed'])