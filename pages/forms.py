import json
from django import forms
from .models import Section


# ---------------------------------------------------------------------------
# Базовый класс — все формы секций наследуют от него.
# Обязательно реализовать: get_schema(), to_data(), from_data()
# ---------------------------------------------------------------------------
class BaseSectionForm(forms.Form):

    @staticmethod
    def get_schema():
        """Возвращает список полей для JS-редактора."""
        return []

    def to_data(self, raw):
        """Из raw POST-словаря → чистый dict для Section.data."""
        return {}

    @staticmethod
    def from_data(data):
        """Из Section.data → начальные значения полей."""
        return {}


# ---------------------------------------------------------------------------
# Текстовый блок (Quill)
# ---------------------------------------------------------------------------
class TextSectionForm(BaseSectionForm):
    # Quill хранит HTML — Django-поле скрытое, JS заполняет его перед сабмитом
    content = forms.CharField(widget=forms.HiddenInput(), required=False)

    @staticmethod
    def get_schema():
        return [
            {
                'name':       'content',
                'label':      'Содержимое',
                'type':       'quill',
                'required':   False,
                'help_text':  '',
                'depends_on': None,
            }
        ]

    def to_data(self, raw):
        return {'content': raw.get('content', '')}

    @staticmethod
    def from_data(data):
        return {'content': data.get('content', '')}


# ---------------------------------------------------------------------------
# Заглушки остальных типов — будут реализованы поэтапно
# ---------------------------------------------------------------------------
class HeroSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'heading', 'label': 'Заголовок', 'type': 'text',
                'required': True, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'subheading', 'label': 'Подзаголовок', 'type': 'text',
                'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'align', 'label': 'Выравнивание', 'type': 'select',
                'options': [
                    {'value': 'left',   'label': 'По левому краю'},
                    {'value': 'center', 'label': 'По центру'},
                    {'value': 'right',  'label': 'По правому краю'},
                ],
                'value': 'left', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'buttons', 'label': 'Кнопки', 'type': 'select',
                'options': [
                    {'value': 'none', 'label': 'Без кнопок'},
                    {'value': 'one',  'label': 'Одна кнопка'},
                    {'value': 'two',  'label': 'Две кнопки'},
                ],
                'value': 'none', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'btn1_text', 'label': 'Текст кнопки 1', 'type': 'text',
                'required': False, 'help_text': '', 
                'depends_on': {'field': 'buttons', 'value': ['one', 'two']},
            },
            {
                'name': 'btn1_url', 'label': 'Ссылка кнопки 1', 'type': 'text',
                'required': False, 'help_text': '',
                'depends_on': {'field': 'buttons', 'value': ['one', 'two']},
            },
            {
                'name': 'btn2_text', 'label': 'Текст кнопки 2', 'type': 'text',
                'required': False, 'help_text': '',
                'depends_on': {'field': 'buttons', 'value': ['two']},
            },
            {
                'name': 'btn2_url', 'label': 'Ссылка кнопки 2', 'type': 'text',
                'required': False, 'help_text': '',
                'depends_on': {'field': 'buttons', 'value': ['two']},
            },
            {
                'name': 'bg_mode', 'label': 'Фон', 'type': 'select',
                'options': [
                    {'value': 'none',         'label': 'Без фото'},
                    {'value': 'image',        'label': 'Фото'},
                    {'value': 'image_dark',   'label': 'Фото + тёмный оверлей'},
                    {'value': 'image_light',  'label': 'Фото + светлый оверлей'},
                ],
                'value': 'none', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'image_id', 'label': 'Фоновое изображение', 'type': 'media',
                'required': False, 'help_text': '',
                'depends_on': {'field': 'bg_mode', 'value': ['image', 'image_dark', 'image_light']},
            },
        ]

    def to_data(self, raw):
        return {
            'heading':    raw.get('heading', ''),
            'subheading': raw.get('subheading', ''),
            'align':      raw.get('align', 'left'),
            'buttons':    raw.get('buttons', 'none'),
            'btn1_text':  raw.get('btn1_text', ''),
            'btn1_url':   raw.get('btn1_url', ''),
            'btn2_text':  raw.get('btn2_text', ''),
            'btn2_url':   raw.get('btn2_url', ''),
            'bg_mode':    raw.get('bg_mode', 'none'),
            'image_id':   raw.get('image_id') or None,
        }

    @staticmethod
    def from_data(data):
        return {
            'heading':    data.get('heading', ''),
            'subheading': data.get('subheading', ''),
            'align':      data.get('align', 'left'),
            'buttons':    data.get('buttons', 'none'),
            'btn1_text':  data.get('btn1_text', ''),
            'btn1_url':   data.get('btn1_url', ''),
            'btn2_text':  data.get('btn2_text', ''),
            'btn2_url':   data.get('btn2_url', ''),
            'bg_mode':    data.get('bg_mode', 'none'),
            'image_id':   data.get('image_id') or '',
        }

class CountersSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name':       'items',
                'label':      'Счётчики',
                'type':       'rows',
                'required':   False,
                'help_text':  '',
                'depends_on': None,
                'row_schema': [
                    {'name': 'value', 'label': 'Значение', 'type': 'text', 'width': 'sm'},
                    {'name': 'label', 'label': 'Подпись',  'type': 'text', 'width': 'md'},
                ],
            }
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except (ValueError, TypeError):
                items = []
        return {
            'items': [
                {
                    'value': str(i.get('value', '')),
                    'label': str(i.get('label', '')),
                }
                for i in items if i.get('value')
            ]
        }

    @staticmethod
    def from_data(data):
        return {'items': data.get('items', [])}

class CardsSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name':       'items',
                'label':      'Карточки',
                'type':       'rows',
                'required':   False,
                'help_text':  '',
                'depends_on': None,
                'row_schema': [
                    {'name': 'icon',  'label': 'Эмодзи', 'type': 'emoji', 'width': 'sm'},
                    {'name': 'title', 'label': 'Заголовок', 'type': 'text', 'width': 'md'},
                    {'name': 'text',  'label': 'Текст', 'type': 'quill', 'width': 'lg'},
                ],
            }
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except (ValueError, TypeError):
                items = []
        return {
            'items': [
                {
                    'icon':  str(i.get('icon',  '')),
                    'title': str(i.get('title', '')),
                    'text':  str(i.get('text',  '')),
                }
                for i in items if i.get('title')
            ]
        }

    @staticmethod
    def from_data(data):
        return {'items': data.get('items', [])}

class TeamSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'items', 'label': 'Участники', 'type': 'rows',
                'required': False, 'help_text': '', 'depends_on': None,
                'row_schema': [
                    {'name': 'photo_id',    'label': 'Фото',       'type': 'media',  'width': 'sm'},
                    {'name': 'name',        'label': 'Имя',        'type': 'text',   'width': 'md'},
                    {'name': 'position',    'label': 'Должность',  'type': 'text',   'width': 'md'},
                    {'name': 'description', 'label': 'Описание',   'type': 'quill',  'width': 'lg'},
                ],
            }
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'items': [
                {
                    'photo_id':    i.get('photo_id') or None,
                    'name':        str(i.get('name', '')),
                    'position':    str(i.get('position', '')),
                    'description': str(i.get('description', '')),
                }
                for i in items if i.get('name')
            ]
        }

    @staticmethod
    def from_data(data):
        return {'items': data.get('items', [])}

class StepsSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'direction', 'label': 'Направление', 'type': 'select',
                'options': [
                    {'value': 'vertical',   'label': 'Вертикально'},
                    {'value': 'horizontal', 'label': 'Горизонтально'},
                ],
                'value': 'vertical', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'items', 'label': 'Шаги', 'type': 'rows',
                'required': False, 'help_text': '', 'depends_on': None,
                'row_schema': [
                    {'name': 'icon',        'label': 'Эмодзи',   'type': 'emoji', 'width': 'sm'},
                    {'name': 'title',       'label': 'Заголовок', 'type': 'text',  'width': 'md'},
                    {'name': 'description', 'label': 'Описание',  'type': 'quill', 'width': 'lg'},
                ],
            },
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'direction': raw.get('direction', 'vertical'),
            'items': [
                {
                    'icon':        str(i.get('icon', '')),
                    'title':       str(i.get('title', '')),
                    'description': str(i.get('description', '')),
                }
                for i in items if i.get('title')
            ],
        }

    @staticmethod
    def from_data(data):
        return {
            'direction': data.get('direction', 'vertical'),
            'items':     data.get('items', []),
        }

class TableSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'style', 'label': 'Стиль таблицы', 'type': 'select',
                'options': [
                    {'value': 'zebra',      'label': 'Полосатые строки'},
                    {'value': 'first_col',  'label': 'Первая колонка жирная'},
                    {'value': 'both',       'label': 'Оба варианта'},
                    {'value': 'plain',      'label': 'Без стиля'},
                ],
                'value': 'zebra', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'table', 'label': 'Таблица', 'type': 'table',
                'required': False, 'help_text': '', 'depends_on': None,
                'value': {'headers': [], 'rows': []},
            },
        ]

    def to_data(self, raw):
        table = raw.get('table', {})
        if isinstance(table, str):
            try: table = json.loads(table)
            except: table = {}
        return {
            'style':   raw.get('style', 'zebra'),
            'headers': table.get('headers', []),
            'rows':    table.get('rows', []),
        }

    @staticmethod
    def from_data(data):
        return {
            'style': data.get('style', 'zebra'),
            'table': {
                'headers': data.get('headers', []),
                'rows':    data.get('rows', []),
            },
        }

class ChartSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'chart_type', 'label': 'Тип диаграммы', 'type': 'select',
                'options': [
                    {'value': 'pie',   'label': 'Круговая'},
                    {'value': 'doughnut', 'label': 'Пончик'},
                    {'value': 'bar',   'label': 'Столбчатая'},
                ],
                'value': 'pie', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'legend_position', 'label': 'Легенда', 'type': 'select',
                'options': [
                    {'value': 'bottom', 'label': 'Снизу'},
                    {'value': 'top',    'label': 'Сверху'},
                    {'value': 'left',   'label': 'Слева'},
                    {'value': 'right',  'label': 'Справа'},
                ],
                'value': 'bottom', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'color_mode', 'label': 'Цвета', 'type': 'select',
                'options': [
                    {'value': 'auto',   'label': 'Авто (системная палитра)'},
                    {'value': 'custom', 'label': 'Настроить вручную'},
                ],
                'value': 'auto', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'items', 'label': 'Данные', 'type': 'rows',
                'required': False, 'help_text': '', 'depends_on': None,
                'row_schema': [
                    {'name': 'label', 'label': 'Подпись', 'type': 'text',  'width': 'md'},
                    {'name': 'value', 'label': 'Значение', 'type': 'text', 'width': 'sm'},
                    {'name': 'color', 'label': 'Цвет',    'type': 'color', 'width': 'sm',
                     'depends_on': {'field': 'color_mode', 'value': ['custom']}},
                ],
            },
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'chart_type':      raw.get('chart_type', 'pie'),
            'legend_position': raw.get('legend_position', 'bottom'),
            'color_mode':      raw.get('color_mode', 'auto'),
            'items': [
                {
                    'label': str(i.get('label', '')),
                    'value': str(i.get('value', '')),
                    'color': str(i.get('color', '')),
                }
                for i in items if i.get('label')
            ],
        }

    @staticmethod
    def from_data(data):
        return {
            'chart_type':      data.get('chart_type', 'pie'),
            'legend_position': data.get('legend_position', 'bottom'),
            'color_mode':      data.get('color_mode', 'auto'),
            'items':           data.get('items', []),
        }

class FormSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'description', 'label': 'Описание формы', 'type': 'textarea',
                'required': False, 'help_text': 'Показывается под заголовком секции',
                'depends_on': None,
            },
            {
                'name': 'button_text', 'label': 'Текст кнопки', 'type': 'text',
                'required': False, 'help_text': '', 'depends_on': None,
                'value': 'Отправить',
            },
            {
                'name': 'success_message', 'label': 'Сообщение после отправки', 'type': 'text',
                'required': False, 'help_text': '', 'depends_on': None,
                'value': 'Спасибо! Мы свяжемся с вами.',
            },
            {
                'name': 'fields', 'label': 'Поля формы', 'type': 'form_fields',
                'required': False, 'help_text': '', 'depends_on': None,
            },
        ]

    def to_data(self, raw):
        fields = raw.get('fields', [])
        if isinstance(fields, str):
            try: fields = json.loads(fields)
            except: fields = []
        return {
            'description':    raw.get('description', ''),
            'button_text':    raw.get('button_text', 'Отправить'),
            'success_message':raw.get('success_message', 'Спасибо! Мы свяжемся с вами.'),
            'fields': [
                {
                    'name':     str(f.get('name', '')),
                    'type':     str(f.get('type', 'text')),
                    'label':    str(f.get('label', '')),
                    'required': bool(f.get('required', False)),
                }
                for f in fields if f.get('name')
            ],
        }

    @staticmethod
    def from_data(data):
        return {
            'description':     data.get('description', ''),
            'button_text':     data.get('button_text', 'Отправить'),
            'success_message': data.get('success_message', 'Спасибо! Мы свяжемся с вами.'),
            'fields':          data.get('fields', []),
        }

class FaqSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'icon_style', 'label': 'Иконка аккордеона', 'type': 'select',
                'options': [
                    {'value': 'arrow', 'label': 'Стрелка ▾'},
                    {'value': 'plus',  'label': 'Плюс / минус +/−'},
                ],
                'value': 'arrow', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'items', 'label': 'Вопросы и ответы', 'type': 'rows',
                'required': False, 'help_text': '', 'depends_on': None,
                'row_schema': [
                    {'name': 'question', 'label': 'Вопрос', 'type': 'text',  'width': 'md'},
                    {'name': 'answer',   'label': 'Ответ',  'type': 'quill', 'width': 'lg'},
                ],
            },
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'icon_style': raw.get('icon_style', 'arrow'),
            'items': [
                {
                    'question': str(i.get('question', '')),
                    'answer':   str(i.get('answer', '')),
                }
                for i in items if i.get('question')
            ],
        }

    @staticmethod
    def from_data(data):
        return {
            'icon_style': data.get('icon_style', 'arrow'),
            'items':      data.get('items', []),
        }

class TestimonialsSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'items', 'label': 'Отзывы', 'type': 'rows',
                'required': False, 'help_text': '', 'depends_on': None,
                'row_schema': [
                    {'name': 'photo_id', 'label': 'Фото',             'type': 'media', 'width': 'sm'},
                    {'name': 'name',     'label': 'Имя',              'type': 'text',  'width': 'md'},
                    {'name': 'role',     'label': 'Должность/компания','type': 'text',  'width': 'md'},
                    {'name': 'text',     'label': 'Текст отзыва',     'type': 'quill', 'width': 'lg'},
                ],
            }
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'items': [
                {
                    'photo_id': i.get('photo_id') or None,
                    'name':     str(i.get('name', '')),
                    'role':     str(i.get('role', '')),

                    'text':     str(i.get('text', '')),
                }
                for i in items if i.get('name')
            ]
        }

    @staticmethod
    def from_data(data):
        return {'items': data.get('items', [])}

class ContactsSectionForm(BaseSectionForm):

    @staticmethod
    def get_schema():
        return [
            {
                'name': 'layout', 'label': 'Расположение карты', 'type': 'select',
                'options': [
                    {'value': 'none',   'label': 'Без карты'},
                    {'value': 'bottom', 'label': 'Карта снизу'},
                    {'value': 'top',    'label': 'Карта сверху'},
                    {'value': 'right',  'label': 'Карта справа'},
                    {'value': 'left',   'label': 'Карта слева'},
                ],
                'value': 'bottom', 'required': False, 'help_text': '', 'depends_on': None,
            },
            {
                'name': 'map_url', 'label': 'Ссылка на карту (Google Maps embed)',
                'type': 'text', 'required': False,
                'help_text': 'Вставьте ссылку из Google Maps → Поделиться → Встроить карту',
                'depends_on': {'field': 'layout', 'value': ['bottom', 'top', 'right', 'left']},
            },
            {
                'name': 'map_label', 'label': 'Заголовок карты',
                'type': 'text', 'required': False, 'help_text': '',
                'depends_on': {'field': 'layout', 'value': ['bottom', 'top', 'right', 'left']},
            },
            {
                'name': 'map_description', 'label': 'Описание под картой',
                'type': 'text', 'required': False, 'help_text': '',
                'depends_on': {'field': 'layout', 'value': ['bottom', 'top', 'right', 'left']},
            },
            {
                'name': 'items', 'label': 'Контактные данные', 'type': 'contacts_rows',
                'required': False, 'help_text': '', 'depends_on': None,
            },
        ]

    def to_data(self, raw):
        items = raw.get('items', [])
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = []
        return {
            'layout':          raw.get('layout', 'bottom'),
            'map_url':         raw.get('map_url', ''),
            'map_label':       raw.get('map_label', ''),
            'map_description': raw.get('map_description', ''),
            'items': [
                {
                    'type':        str(i.get('type', 'phone')),
                    'label':       str(i.get('label', '')),
                    'value':       str(i.get('value', '')),
                    'description': str(i.get('description', '')),
                }
                for i in items if i.get('value')
            ],
        }

    @staticmethod
    def from_data(data):
        return {
            'layout':          data.get('layout', 'bottom'),
            'map_url':         data.get('map_url', ''),
            'map_label':       data.get('map_label', ''),
            'map_description': data.get('map_description', ''),
            'items':           data.get('items', []),
        }


# ---------------------------------------------------------------------------
# Реестр: тип секции → класс формы
# ---------------------------------------------------------------------------
SECTION_FORM_MAP = {
    'hero':         HeroSectionForm,
    'text':         TextSectionForm,
    'counters':     CountersSectionForm,
    'cards':        CardsSectionForm,
    'team':         TeamSectionForm,
    'steps':        StepsSectionForm,
    'table':        TableSectionForm,
    'chart':    ChartSectionForm,
    'form':         FormSectionForm,
    'faq':          FaqSectionForm,
    'testimonials': TestimonialsSectionForm,
    'contacts':     ContactsSectionForm,
}


# ---------------------------------------------------------------------------
# Форма секции для Django admin.
# Содержит только базовые поля + скрытый section_data (JSON).
# Всё остальное рендерит JS.
# ---------------------------------------------------------------------------
class SectionAdminForm(forms.ModelForm):

    section_data = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'section-data-input'}),
        required=False,
    )

    class Meta:
        model  = Section
        fields = ['page', 'type', 'title', 'is_visible', 'section_data']

    def save(self, commit=True):
        obj = super().save(commit=False)
        raw = self.cleaned_data.get('section_data', '').strip()

        if raw:
            try:
                raw_dict      = json.loads(raw)
                form_class    = SECTION_FORM_MAP.get(obj.type)
                if form_class:
                    obj.data = form_class().to_data(raw_dict)
                else:
                    obj.data = raw_dict
            except (ValueError, TypeError):
                obj.data = obj.data or {}
        else:
            obj.data = obj.data or {}

        if commit:
            obj.save()
        return obj