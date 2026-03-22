from django import forms
from .models import Section


class HeroSectionForm(forms.Form):
    heading     = forms.CharField(label='Заголовок', max_length=200)
    subheading  = forms.CharField(label='Подзаголовок', max_length=300, required=False)
    button_text = forms.CharField(label='Текст кнопки', max_length=100, required=False)
    button_url  = forms.CharField(label='Ссылка кнопки', max_length=200, required=False)
    # ID файла из медиабиблиотеки — выбирается через JS-пикер
    image_id    = forms.IntegerField(label='Фоновое изображение (ID)', required=False)

    def to_data(self):
        d = self.cleaned_data
        return {
            'heading':     d.get('heading', ''),
            'subheading':  d.get('subheading', ''),
            'button_text': d.get('button_text', ''),
            'button_url':  d.get('button_url', ''),
            'image_id':    d.get('image_id') or None,
        }

    @staticmethod
    def from_data(data):
        return {
            'heading':     data.get('heading', ''),
            'subheading':  data.get('subheading', ''),
            'button_text': data.get('button_text', ''),
            'button_url':  data.get('button_url', ''),
            'image_id':    data.get('image_id') or '',
        }


class TextSectionForm(forms.Form):
    content = forms.CharField(label='Содержимое', widget=forms.Textarea(attrs={'rows': 6}))

    def to_data(self):
        return {'content': self.cleaned_data.get('content', '')}

    @staticmethod
    def from_data(data):
        return {'content': data.get('content', '')}


class CountersSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Счётчики',
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Каждый с новой строки: значение|подпись\nПример: 150|Проектов',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            if '|' in line:
                value, label = line.split('|', 1)
                items.append({'value': value.strip(), 'label': label.strip()})
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('value', '')}|{i.get('label', '')}" for i in items
        )}


class CardsSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Карточки',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Каждая с новой строки: иконка|заголовок|текст\nПример: ★|Качество|Проверенные материалы',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            parts = line.split('|', 2)
            if len(parts) >= 2:
                items.append({
                    'icon':  parts[0].strip(),
                    'title': parts[1].strip(),
                    'text':  parts[2].strip() if len(parts) > 2 else '',
                })
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('icon', '')}|{i.get('title', '')}|{i.get('text', '')}"
            for i in items
        )}


class TeamSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Участники',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Каждый с новой строки: имя|должность|описание\nПример: Иван Петров|Директор|Основатель',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            parts = line.split('|', 2)
            if parts and parts[0].strip():
                items.append({
                    'name':        parts[0].strip(),
                    'position':    parts[1].strip() if len(parts) > 1 else '',
                    'description': parts[2].strip() if len(parts) > 2 else '',
                })
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('name', '')}|{i.get('position', '')}|{i.get('description', '')}"
            for i in items
        )}


class StepsSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Шаги',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Каждый с новой строки: заголовок|описание\nПример: Заявка|Вы оставляете заявку на сайте',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            parts = line.split('|', 1)
            if parts and parts[0].strip():
                items.append({
                    'title':       parts[0].strip(),
                    'description': parts[1].strip() if len(parts) > 1 else '',
                })
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('title', '')}|{i.get('description', '')}"
            for i in items
        )}


class TableSectionForm(forms.Form):
    headers_raw = forms.CharField(
        label='Заголовки столбцов (через |)',
        help_text='Пример: Услуга|Срок|Цена',
        required=False,
    )
    rows_raw = forms.CharField(
        label='Строки таблицы',
        widget=forms.Textarea(attrs={'rows': 8}),
        help_text='Каждая строка с новой строки, ячейки через |\nПример: Фундамент|14 дней|150 000 ₽',
        required=False,
    )

    def to_data(self):
        headers = [h.strip() for h in self.cleaned_data.get('headers_raw', '').split('|') if h.strip()]
        rows = []
        for line in self.cleaned_data.get('rows_raw', '').strip().splitlines():
            if line.strip():
                rows.append([cell.strip() for cell in line.split('|')])
        return {'headers': headers, 'rows': rows}

    @staticmethod
    def from_data(data):
        return {
            'headers_raw': '|'.join(data.get('headers', [])),
            'rows_raw':    '\n'.join('|'.join(row) for row in data.get('rows', [])),
        }


class ChartPieSectionForm(forms.Form):
    chart_title = forms.CharField(label='Заголовок диаграммы', required=False)
    items_raw   = forms.CharField(
        label='Данные диаграммы',
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Каждый с новой строки: подпись|значение\nПример: Онлайн|45',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            if '|' in line:
                label, value = line.split('|', 1)
                items.append({'label': label.strip(), 'value': value.strip()})
        return {'title': self.cleaned_data.get('chart_title', ''), 'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {
            'chart_title': data.get('title', ''),
            'items_raw':   '\n'.join(
                f"{i.get('label', '')}|{i.get('value', '')}" for i in items
            ),
        }


class FormSectionForm(forms.Form):
    fields_raw = forms.CharField(
        label='Поля формы',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Каждое поле с новой строки: имя|тип|подпись|обязательное\nПример: name|text|Ваше имя|true',
        required=False,
    )

    def to_data(self):
        fields = []
        for line in self.cleaned_data.get('fields_raw', '').strip().splitlines():
            parts = line.split('|', 3)
            if len(parts) == 4:
                fields.append({
                    'name':     parts[0].strip(),
                    'type':     parts[1].strip(),
                    'label':    parts[2].strip(),
                    'required': parts[3].strip().lower() == 'true',
                })
        return {'fields': fields}

    @staticmethod
    def from_data(data):
        fields = data.get('fields', [])
        return {'fields_raw': '\n'.join(
            f"{f.get('name', '')}|{f.get('type', '')}|{f.get('label', '')}|{str(f.get('required', False)).lower()}"
            for f in fields
        )}


class FaqSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Вопросы и ответы',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Каждый с новой строки: вопрос|ответ\nПример: Как оставить заявку?|Заполните форму на сайте',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            if '|' in line:
                question, answer = line.split('|', 1)
                items.append({'question': question.strip(), 'answer': answer.strip()})
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('question', '')}|{i.get('answer', '')}" for i in items
        )}


class TestimonialsSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Отзывы',
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Каждый с новой строки: имя|текст\nПример: Анна К.|Отличная работа, всё в срок!',
        required=False,
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data.get('items_raw', '').strip().splitlines():
            if '|' in line:
                name, text = line.split('|', 1)
                items.append({'name': name.strip(), 'text': text.strip()})
        return {'items': items}

    @staticmethod
    def from_data(data):
        items = data.get('items', [])
        return {'items_raw': '\n'.join(
            f"{i.get('name', '')}|{i.get('text', '')}" for i in items
        )}


class ContactsSectionForm(forms.Form):
    """Новая секция: контактная информация в произвольном месте страницы."""
    address   = forms.CharField(label='Адрес', widget=forms.Textarea(attrs={'rows': 2}), required=False)
    phone     = forms.CharField(label='Телефон', max_length=100, required=False)
    email     = forms.EmailField(label='Email', required=False)
    hours     = forms.CharField(label='Режим работы', max_length=200, required=False)
    map_url   = forms.URLField(label='Ссылка на карту (Google Maps embed)', max_length=500, required=False)

    def to_data(self):
        d = self.cleaned_data
        return {
            'address': d.get('address', ''),
            'phone':   d.get('phone', ''),
            'email':   d.get('email', ''),
            'hours':   d.get('hours', ''),
            'map_url': d.get('map_url', ''),
        }

    @staticmethod
    def from_data(data):
        return {
            'address': data.get('address', ''),
            'phone':   data.get('phone', ''),
            'email':   data.get('email', ''),
            'hours':   data.get('hours', ''),
            'map_url': data.get('map_url', ''),
        }


# ---------------------------------------------------------------------------
# Единый реестр: тип → класс формы.
# Используется в SectionAdminForm и в AJAX-view section_fields.
# ---------------------------------------------------------------------------
SECTION_FORM_MAP = {
    'hero':         HeroSectionForm,
    'text':         TextSectionForm,
    'counters':     CountersSectionForm,
    'cards':        CardsSectionForm,
    'team':         TeamSectionForm,
    'steps':        StepsSectionForm,
    'table':        TableSectionForm,
    'chart_pie':    ChartPieSectionForm,
    'form':         FormSectionForm,
    'faq':          FaqSectionForm,
    'testimonials': TestimonialsSectionForm,
    'contacts':     ContactsSectionForm,
}


# ---------------------------------------------------------------------------
# Форма секции для Django admin.
# Базовые поля (page, type, title, is_visible) — всегда видны.
# Поля конкретного типа подгружаются через AJAX и рендерятся JS-редактором.
# При сохранении скрытый <textarea id="section-data-input"> содержит JSON,
# который мы кладём в obj.data.
# ---------------------------------------------------------------------------
class SectionAdminForm(forms.ModelForm):

    # Скрытое поле — JSON с данными секции, заполняется JS перед сабмитом
    section_data = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'section-data-input'}),
        required=False,
    )

    class Meta:
        model  = Section
        fields = ['page', 'type', 'title', 'is_visible', 'section_data']

    def save(self, commit=True):
        import json
        obj = super().save(commit=False)
        raw = self.cleaned_data.get('section_data', '').strip()
        if raw:
            try:
                obj.data = json.loads(raw)
            except (ValueError, TypeError):
                obj.data = obj.data or {}
        else:
            obj.data = obj.data or {}
        if commit:
            obj.save()
        return obj