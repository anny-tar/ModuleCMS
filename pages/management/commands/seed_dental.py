"""
Команда наполнения БД демо-данными стоматологического центра «ДентаПро».

Использование:
    python manage.py seed_dental
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Наполняет БД демо-данными стоматологии «ДентаПро»'

    def handle(self, *args, **options):
        from pages.management.commands.seed_base import clear_all, create_users, create_appearance

        self.stdout.write('Очистка БД...')
        clear_all()

        self.stdout.write('Создание пользователей...')
        create_users()

        self.stdout.write('Создание оформления...')
        theme, font = create_appearance(
            primary='#0891b2', background='#ffffff', surface='#f0f9ff',
            accent='#0e7490', text='#0c1a2e',
            font_name='Nunito', font_google='Nunito',
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
            '\nДентаПро готов. http://127.0.0.1:8000/\n'
            'admin / admin1234\n'
            'director / director1234\n'
            'manager / manager1234\n'
            'editor / editor1234'
        ))

    def _settings(self, theme, font):
        from appearance.models import SiteSettings
        SiteSettings.objects.create(
            pk=1, site_name='ДентаПро',
            active_theme=theme, active_font=font,
            contact_address='г. Москва, ул. Тверская, д. 18, этаж 2',
            contact_phone='+7 (495) 987-65-43',
            contact_email='info@dentapro.ru',
            contact_hours='Пн–Пт: 9:00–21:00, Сб–Вс: 10:00–18:00',
        )

    def _pages(self):
        from pages.models import Page, Section, PageType

        home = Page.objects.create(
            title='Главная', slug='glavnaya', page_type=PageType.DEFAULT,
            is_published=True, order=0,
            seo_title='ДентаПро — стоматология без боли в Москве',
        )
        o = 0

        Section.objects.create(page=home, type='hero', order=o, is_visible=True, data={
            'heading': 'Здоровые зубы — красивая улыбка',
            'subheading': 'Современная стоматология без боли и страха. Передовые технологии, опытные врачи, комфортная атмосфера. Консультация бесплатно.',
            'button_text': 'Записаться на приём',
            'button_url': '#section-form',
        }); o += 1

        Section.objects.create(page=home, type='text', title='О клинике ДентаПро', order=o, is_visible=True, data={
            'content': 'ДентаПро — частная стоматологическая клиника в центре Москвы. Работаем с 2010 года. За это время приняли более 20 000 пациентов и провели свыше 50 000 процедур.\n\nМы принципиально не практикуем «принудительное лечение» — предлагаем только то, что действительно нужно. Перед любым лечением врач составляет подробный план с описанием каждого этапа и фиксированной стоимостью.\n\nВ клинике работают 12 специалистов с опытом от 10 лет. Все врачи регулярно проходят обучение в России и за рубежом.',
        }); o += 1

        Section.objects.create(page=home, type='counters', title='ДентаПро в цифрах', order=o, is_visible=True, data={
            'items': [
                {'value': '12',     'label': 'Врачей-специалистов'},
                {'value': '15',     'label': 'Лет на рынке'},
                {'value': '20 000', 'label': 'Пациентов за всё время'},
                {'value': '98%',    'label': 'Рекомендуют клинику'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='cards', title='Наши преимущества', order=o, is_visible=True, data={
            'items': [
                {'icon': '😌', 'title': 'Лечение без боли',       'text': 'Современные анестетики и седация. Лечение даже для самых тревожных пациентов.'},
                {'icon': '🔬', 'title': 'Передовые технологии',   'text': '3D-диагностика, цифровые слепки, лазерное лечение. Точность и безопасность.'},
                {'icon': '👨‍⚕️', 'title': 'Опытные специалисты', 'text': 'Стаж каждого врача — от 10 лет. Ежегодное обучение в ведущих клиниках.'},
                {'icon': '🦷', 'title': 'Гарантия на работы',     'text': 'На пломбы — 3 года, на коронки — 7 лет, на импланты — 10 лет.'},
                {'icon': '🕐', 'title': 'Удобный график',         'text': 'Ежедневно с 9:00 до 21:00. Принимаем в выходные без наценки.'},
                {'icon': '💳', 'title': 'Рассрочка 0%',           'text': 'Оплата в рассрочку на 12 месяцев без банков и переплат.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='text', title='Как проходит первый визит', order=o, is_visible=True, data={
            'content': 'Первый визит начинается с бесплатной консультации. Врач проводит осмотр, при необходимости делает снимок или КТ.\n\nПо результатам осмотра составляется план лечения с конкретными цифрами — никаких «от 5 000 рублей». Если объём лечения большой, разбиваем на этапы по приоритету: сначала устраняем острую боль, затем проводим плановое лечение в удобном темпе.',
        }); o += 1

        Section.objects.create(page=home, type='steps', title='Как записаться', order=o, is_visible=True, data={
            'items': [
                {'title': 'Оставьте заявку',      'description': 'Форма на сайте, телефон или мессенджер. Отвечаем в течение 15 минут.'},
                {'title': 'Выберите время',        'description': 'Администратор предложит удобное время. Напомним о визите SMS.'},
                {'title': 'Консультация',          'description': 'Осмотр, снимок при необходимости. Бесплатно.'},
                {'title': 'План лечения',          'description': 'Подробный план с фиксированной стоимостью каждого этапа.'},
                {'title': 'Лечение и наблюдение',  'description': 'Лечение по плану. Через 6 месяцев — бесплатный профилактический осмотр.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='testimonials', title='Отзывы пациентов', order=o, is_visible=True, data={
            'items': [
                {'name': 'Екатерина М.', 'text': 'Боялась стоматологов всю жизнь. В ДентаПро всё иначе — не больно, врач объяснял каждый шаг. Теперь хожу сюда и привела всю семью.'},
                {'name': 'Андрей К.',    'text': 'Поставили имплант. Прошло 8 месяцев — всё отлично. Цена честная, никаких скрытых доплат.'},
                {'name': 'Мария П.',     'text': 'Выравнивали зубы ребёнку брекетами. Детский стоматолог нашла подход, ребёнок не боялся. Результат превзошёл ожидания.'},
                {'name': 'Дмитрий В.',   'text': 'Отбеливание ZOOM — 8 тонов за полтора часа. Держится уже год. Сервис на высоте.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='faq', title='Часто задаваемые вопросы', order=o, is_visible=True, data={
            'items': [
                {'question': 'Больно ли лечить зубы?',    'answer': 'Нет. Используем анестетики последнего поколения. Для тревожных пациентов доступна медикаментозная седация.'},
                {'question': 'Сколько стоит лечение?',    'answer': 'Консультация и план лечения — бесплатно. Лечение кариеса от 4 500 ₽. Точная стоимость — после осмотра.'},
                {'question': 'Принимаете ли детей?',      'answer': 'Да, с 3 лет. Детский кабинет с игрушками и мультфильмами. Специальная методика безболезненного лечения молочных зубов.'},
                {'question': 'Работаете ли по ДМС?',      'answer': 'Да. Принимаем РЕСО, Ингосстрах, ВСК, Альфастрахование. Уточните наличие вашей страховой по телефону.'},
                {'question': 'Какая гарантия на лечение?','answer': 'Пломбы — 3 года, коронки — 7 лет, импланты — 10 лет. При дефекте в гарантийный период — переделываем бесплатно.'},
            ]
        }); o += 1

        Section.objects.create(page=home, type='form', title='Запись на приём', order=o, is_visible=True, data={
            'fields': [
                {'name': 'name',      'type': 'text',     'label': 'Ваше имя',            'required': True},
                {'name': 'phone',     'type': 'tel',      'label': 'Телефон',             'required': True},
                {'name': 'direction', 'type': 'text',     'label': 'Направление лечения', 'required': False},
                {'name': 'time',      'type': 'text',     'label': 'Удобное время',       'required': False},
                {'name': 'message',   'type': 'textarea', 'label': 'Комментарий',         'required': False},
            ]
        })

        services = Page.objects.create(title='Услуги и цены', slug='uslugi', page_type=PageType.DEFAULT, is_published=True, order=1)
        o = 0
        Section.objects.create(page=services, type='text', title='Направления лечения', order=o, is_visible=True, data={'content': 'В ДентаПро представлены все основные направления стоматологии. Большинство проблем можно решить в одной клинике без направлений к сторонним специалистам.'}); o += 1
        Section.objects.create(page=services, type='cards', title='Наши услуги', order=o, is_visible=True, data={'items': [
            {'icon': '🦷', 'title': 'Терапия',              'text': 'Лечение кариеса, пульпита, периодонтита. Световые пломбы и реставрации.'},
            {'icon': '🔩', 'title': 'Имплантация',          'text': 'Под ключ. Немедленная нагрузка — коронка в день операции.'},
            {'icon': '👑', 'title': 'Ортопедия',            'text': 'Коронки, мосты, виниры. Металлокерамика и безметалловая керамика.'},
            {'icon': '📐', 'title': 'Ортодонтия',           'text': 'Брекеты и элайнеры. Лечение детей и взрослых.'},
            {'icon': '✨', 'title': 'Отбеливание',          'text': 'ZOOM и Beyond. До 10 тонов за 1,5 часа.'},
            {'icon': '🩺', 'title': 'Хирургия',             'text': 'Удаление зубов любой сложности, включая зубы мудрости.'},
            {'icon': '🧒', 'title': 'Детская стоматология', 'text': 'Лечение с 3 лет. Профилактика кариеса.'},
            {'icon': '🧴', 'title': 'Гигиена',              'text': 'Профессиональная чистка, Air Flow, фторирование.'},
        ]}); o += 1
        Section.objects.create(page=services, type='table', title='Прайс-лист', order=o, is_visible=True, data={
            'headers': ['Услуга', 'Цена от'],
            'rows': [
                ['Консультация',             'Бесплатно'], ['Лечение кариеса',   '4 500 ₽'],
                ['Лечение пульпита (1 канал)','8 000 ₽'],  ['Удаление зуба',     '3 500 ₽'],
                ['Имплант под ключ',         '55 000 ₽'], ['Коронка керамика',  '22 000 ₽'],
                ['Винир',                    '25 000 ₽'],  ['Отбеливание ZOOM',  '25 000 ₽'],
                ['Брекеты (комплект)',        '85 000 ₽'], ['Профчистка',        '5 500 ₽'],
            ]
        }); o += 1
        Section.objects.create(page=services, type='text', title='О стоимости', order=o, is_visible=True, data={'content': 'Цены указаны от минимального значения. Окончательная стоимость — после осмотра.\n\nМы не практикуем дополнительные продажи во время лечения. Если обнаружится дополнительная проблема — согласуем с вами до начала.\n\nДля пенсионеров и многодетных семей — скидка 10% на терапевтическое лечение.'}); o += 1
        Section.objects.create(page=services, type='chart_pie', title='Структура обращений', order=o, is_visible=True, data={'title': 'По направлениям за 2024 год', 'items': [
            {'label': 'Терапия', 'value': '38'}, {'label': 'Ортопедия', 'value': '22'},
            {'label': 'Имплантация', 'value': '15'}, {'label': 'Ортодонтия', 'value': '12'},
            {'label': 'Гигиена', 'value': '8'}, {'label': 'Хирургия', 'value': '5'},
        ]}); o += 1
        Section.objects.create(page=services, type='form', title='Записаться на консультацию', order=o, is_visible=True, data={'fields': [
            {'name': 'name', 'type': 'text', 'label': 'Ваше имя', 'required': True},
            {'name': 'phone', 'type': 'tel', 'label': 'Телефон', 'required': True},
            {'name': 'service', 'type': 'text', 'label': 'Услуга', 'required': False},
        ]})

        doctors = Page.objects.create(title='Врачи', slug='vrachi', page_type=PageType.DEFAULT, is_published=True, order=2)
        o = 0
        Section.objects.create(page=doctors, type='text', title='Наша команда', order=o, is_visible=True, data={'content': 'Все врачи ДентаПро — специалисты с профильным образованием и стажем не менее 10 лет. Ежегодно каждый врач проходит не менее 40 часов повышения квалификации.'}); o += 1
        Section.objects.create(page=doctors, type='team', title='Специалисты клиники', order=o, is_visible=True, data={'items': [
            {'name': 'Соколов Игорь Владимирович', 'position': 'Главный врач, имплантолог', 'description': 'Стаж 20 лет. Провёл более 3 000 имплантаций. Сертифицирован Nobel Biocare и Straumann.'},
            {'name': 'Белова Анна Сергеевна',      'position': 'Терапевт, эстетист',        'description': 'Стаж 14 лет. Специализируется на эстетической реставрации.'},
            {'name': 'Козлов Дмитрий Андреевич',   'position': 'Ортодонт',                  'description': 'Стаж 12 лет. Брекеты и элайнеры у детей и взрослых. Стажировался в Германии.'},
            {'name': 'Морозова Елена Петровна',    'position': 'Детский стоматолог',        'description': 'Стаж 10 лет. Принимает с 3 лет. Методика безболезненного лечения.'},
            {'name': 'Тихонов Алексей Борисович',  'position': 'Хирург-пародонтолог',       'description': 'Стаж 16 лет. Синус-лифтинг, костная пластика, сложные удаления.'},
            {'name': 'Громова Наталья Игоревна',   'position': 'Ортопед',                   'description': 'Стаж 13 лет. Протезирование на имплантах, коронки, виниры.'},
        ]}); o += 1
        Section.objects.create(page=doctors, type='counters', title='Квалификация', order=o, is_visible=True, data={'items': [
            {'value': '12', 'label': 'Специалистов'}, {'value': '120', 'label': 'Часов обучения в год'},
            {'value': '8', 'label': 'Стран стажировок'}, {'value': '3', 'label': 'Преподавателя вузов'},
        ]}); o += 1
        Section.objects.create(page=doctors, type='form', title='Записаться к врачу', order=o, is_visible=True, data={'fields': [
            {'name': 'name', 'type': 'text', 'label': 'Ваше имя', 'required': True},
            {'name': 'phone', 'type': 'tel', 'label': 'Телефон', 'required': True},
            {'name': 'doctor', 'type': 'text', 'label': 'Врач', 'required': False},
            {'name': 'time', 'type': 'text', 'label': 'Удобное время', 'required': False},
        ]})

        Page.objects.create(title='Новости', slug='novosti', page_type=PageType.NEWS, is_published=True, order=3)
        Page.objects.create(title='Галерея', slug='galereya', page_type=PageType.GALLERY, is_published=True, order=4)
        Page.objects.create(title='Контакты', slug='kontakty', page_type=PageType.CONTACTS, is_published=True, order=5)

    def _news(self):
        from news.models import Category, Article
        cat_clinic = Category.objects.create(name='Новости клиники',  order=0)
        cat_tips   = Category.objects.create(name='Советы пациентам', order=1)
        cat_promo  = Category.objects.create(name='Акции',            order=2)
        Article.objects.create(title='Новый 3D-томограф Planmeca ProMax в клинике', slug='novyj-3d-tomograf', category=cat_clinic, is_published=True, published_at=timezone.now().replace(month=2, day=10), announce='Точная 3D-диагностика за 14 секунд с минимальной дозой излучения.', content='В феврале 2025 года в ДентаПро установлен конусно-лучевой томограф Planmeca ProMax 3D.\n\nСнимок делается за 14 секунд при минимальной дозе излучения. Детализация — 0,075 мм на воксель. Это позволяет точно планировать имплантацию: врач видит нервные каналы, сосуды, плотность и толщину кости.\n\nПлан имплантации теперь строится в 3D ещё до операции. Риски сведены к минимуму.')
        Article.objects.create(title='5 ошибок при чистке зубов', slug='5-oshibok-chistka', category=cat_tips, is_published=True, published_at=timezone.now().replace(month=1, day=25), announce='90% людей чистят зубы неправильно. Объясняем основные ошибки.', content='Горизонтальные движения щёткой — самая распространённая ошибка. Правильная техника: выметающие движения от десны к краю зуба под углом 45°.\n\nМало времени. Достаточная чистка — 2 минуты. Большинство тратит 40 секунд.\n\nЖёсткая щётка стирает эмаль. Оптимально — мягкая или средняя.\n\nЗабывают о языке. На нём до 80% бактерий, вызывающих запах. Чистите скребком ежедневно.\n\nНе меняют щётку. Меняйте каждые 3 месяца — изношенная чистит на 30% хуже.')
        Article.objects.create(title='Акция: скидка 20% на профчистку в марте', slug='akciya-mart', category=cat_promo, is_published=True, published_at=timezone.now().replace(month=3, day=1), announce='Скидка 20% на профессиональную гигиену для новых пациентов до 31 марта.', content='В марте 2025 года скидка 20% на профессиональную гигиену полости рта для новых пациентов.\n\n4 400 ₽ вместо 5 500 ₽. В стоимость входит: ультразвуковая чистка, Air Flow, полировка, фторлак.\n\nАкция действует с 1 по 31 марта 2025 года. При записи назовите код «УЛЫБКА».')
        Article.objects.create(title='Имплантация за один день', slug='implantaciya-za-den', category=cat_clinic, is_published=True, published_at=timezone.now().replace(month=2, day=20), announce='Немедленная нагрузка: уходите с временной коронкой в день установки импланта.', content='Технология немедленной нагрузки позволяет уйти домой с зубом в день операции.\n\nИмплант устанавливается сразу после удаления зуба. В тот же день фиксируется временная коронка.\n\nЧерез 3–4 месяца временная коронка заменяется постоянной.\n\nМетод подходит не всем — необходимы достаточная плотность кости и здоровье дёсен. Врач определяет возможность по КТ-снимку.')

    def _gallery(self):
        from gallery.models import Album
        Album.objects.create(title='Клиника и кабинеты',        description='Оборудование и атмосфера ДентаПро.',            order=0, is_published=True)
        Album.objects.create(title='Работы по имплантации',     description='Результаты до и после (с разрешения пациентов).', order=1, is_published=True)
        Album.objects.create(title='Эстетическая стоматология', description='Виниры, отбеливание, реставрация.',               order=2, is_published=True)
        Album.objects.create(title='Ортодонтия — до и после',   description='Брекеты и элайнеры. Результаты лечения.',         order=3, is_published=True)

    def _leads(self):
        from leads.models import LeadSubmission
        for l in [
            {'data': {'name': 'Ольга Смирнова',    'phone': '+7 (916) 111-22-33', 'direction': 'Имплантация',         'time': 'Утром в будни', 'message': 'Консультация по импланту нижней челюсти'}, 'is_viewed': False},
            {'data': {'name': 'Виктор Попов',      'phone': '+7 (903) 444-55-66', 'direction': 'Лечение кариеса',     'time': 'Вечером',       'message': ''},                                        'is_viewed': True},
            {'data': {'name': 'Светлана Новикова', 'phone': '+7 (925) 777-00-11', 'direction': 'Детская стоматология','time': 'Выходные',      'message': 'Ребёнку 6 лет, первый визит'},             'is_viewed': False},
            {'data': {'name': 'Артём Козлов',      'phone': '+7 (499) 321-00-99', 'direction': 'Отбеливание',         'time': 'Любое',         'message': 'Интересует ZOOM'},                         'is_viewed': True},
            {'data': {'name': 'Ирина Белова',      'phone': '+7 (926) 888-77-66', 'direction': 'Брекеты',             'time': 'Утром',         'message': 'Исправить прикус, взрослая'},              'is_viewed': False},
        ]:
            LeadSubmission.objects.create(section_id=1, data=l['data'], is_viewed=l['is_viewed'])