from django import forms
from .models import Section


class HeroSectionForm(forms.Form):
    heading     = forms.CharField(label='Заголовок', max_length=200)
    subheading  = forms.CharField(label='Подзаголовок', max_length=300, required=False)
    button_text = forms.CharField(label='Текст кнопки', max_length=100, required=False)
    button_url  = forms.CharField(label='Ссылка кнопки', max_length=200, required=False)

    def to_data(self):
        d = self.cleaned_data
        return {
            'heading':     d.get('heading', ''),
            'subheading':  d.get('subheading', ''),
            'button_text': d.get('button_text', ''),
            'button_url':  d.get('button_url', ''),
        }

    @staticmethod
    def from_data(data):
        return {
            'heading':     data.get('heading', ''),
            'subheading':  data.get('subheading', ''),
            'button_text': data.get('button_text', ''),
            'button_url':  data.get('button_url', ''),
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
}


# ---------------------------------------------------------------------------
class SectionAdminForm(forms.ModelForm):

    class Meta:
        model  = Section
        fields = ['page', 'type', 'title', 'is_visible']

    def __init__(self, *args, **kwargs):
        import copy
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        post_data    = args[0] if args and hasattr(args[0], 'get') else None
        current_type = (post_data.get('type') if post_data else None) or (instance.type if instance else None)

        if not current_type or current_type not in SECTION_FORM_MAP:
            return

        form_class    = SECTION_FORM_MAP[current_type]
        initial_typed = {}
        if instance and instance.data and not post_data and hasattr(form_class, 'from_data'):
            initial_typed = form_class.from_data(instance.data)

        for name, field in form_class.base_fields.items():
            f = copy.deepcopy(field)
            f.required = False
            self.fields[name] = f
            if name in initial_typed:
                self.initial[name] = initial_typed[name]

    def save(self, commit=True):
        obj = super().save(commit=False)
        if obj.type in SECTION_FORM_MAP:
            form_class = SECTION_FORM_MAP[obj.type]
            typed_data = {
                name: self.cleaned_data[name]
                for name in form_class.base_fields
                if name in self.cleaned_data
            }
            if typed_data:
                typed_form = form_class(data=typed_data)
                typed_form.is_valid()
                obj.data = typed_form.to_data() if hasattr(typed_form, 'to_data') else typed_data
            else:
                obj.data = obj.data or {}
        if commit:
            obj.save()
        return obj