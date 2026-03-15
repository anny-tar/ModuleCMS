from django import forms


class HeroSectionForm(forms.Form):
    heading     = forms.CharField(label='Заголовок', max_length=200)
    subheading  = forms.CharField(label='Подзаголовок', max_length=300,
                                  required=False)
    button_text = forms.CharField(label='Текст кнопки', max_length=100,
                                  required=False)
    button_url  = forms.CharField(label='Ссылка кнопки', max_length=200,
                                  required=False)


class TextSectionForm(forms.Form):
    content = forms.CharField(label='Содержимое', widget=forms.Textarea)


class CountersSectionForm(forms.Form):
    # Счётчики вводятся построчно: значение|подпись
    items_raw = forms.CharField(
        label='Счётчики (каждый с новой строки: значение|подпись)',
        widget=forms.Textarea,
        help_text='Пример: 150|Проектов\n18|Лет на рынке\n3|Региона'
    )

    def to_data(self):
        # Преобразование текста в список словарей для JSONField
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            if '|' in line:
                value, label = line.split('|', 1)
                items.append({'value': value.strip(), 'label': label.strip()})
        return {'items': items}


class CardsSectionForm(forms.Form):
    # Карточки вводятся построчно: иконка|заголовок|текст
    items_raw = forms.CharField(
        label='Карточки (каждая с новой строки: иконка|заголовок|текст)',
        widget=forms.Textarea,
        help_text='Пример: ★|Качество|Работаем только с проверенными материалами'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            parts = line.split('|', 2)
            if len(parts) == 3:
                items.append({
                    'icon':  parts[0].strip(),
                    'title': parts[1].strip(),
                    'text':  parts[2].strip(),
                })
        return {'items': items}

class TeamSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Участники (каждый с новой строки: имя|должность|описание)',
        widget=forms.Textarea,
        help_text='Пример: Иван Петров|Директор|Основатель компании'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            parts = line.split('|', 2)
            if len(parts) >= 2:
                items.append({
                    'name':        parts[0].strip(),
                    'position':    parts[1].strip(),
                    'description': parts[2].strip() if len(parts) == 3 else '',
                })
        return {'items': items}


class StepsSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Шаги (каждый с новой строки: заголовок|описание)',
        widget=forms.Textarea,
        help_text='Пример: Заявка|Вы оставляете заявку на сайте'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            parts = line.split('|', 1)
            if parts:
                items.append({
                    'title':       parts[0].strip(),
                    'description': parts[1].strip() if len(parts) == 2 else '',
                })
        return {'items': items}


class TableSectionForm(forms.Form):
    headers_raw = forms.CharField(
        label='Заголовки столбцов (через |)',
        help_text='Пример: Услуга|Срок|Цена'
    )
    rows_raw = forms.CharField(
        label='Строки (каждая с новой строки, ячейки через |)',
        widget=forms.Textarea,
        help_text='Пример: Фундамент|14 дней|150 000 ₽'
    )

    def to_data(self):
        headers = [h.strip() for h in self.cleaned_data['headers_raw'].split('|')]
        rows = []
        for line in self.cleaned_data['rows_raw'].strip().splitlines():
            rows.append([cell.strip() for cell in line.split('|')])
        return {'headers': headers, 'rows': rows}


class ChartPieSectionForm(forms.Form):
    chart_title = forms.CharField(label='Заголовок диаграммы', required=False)
    items_raw   = forms.CharField(
        label='Данные (каждый с новой строки: подпись|значение)',
        widget=forms.Textarea,
        help_text='Пример: Онлайн|45\nОфлайн|35\nГибрид|20'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            if '|' in line:
                label, value = line.split('|', 1)
                items.append({'label': label.strip(), 'value': value.strip()})
        return {'title': self.cleaned_data['chart_title'], 'items': items}


class FormSectionForm(forms.Form):
    fields_raw = forms.CharField(
        label='Поля формы (каждое с новой строки: имя|тип|подпись|обязательное)',
        widget=forms.Textarea,
        help_text='Пример: name|text|Ваше имя|true\nphone|tel|Телефон|true\nmessage|textarea|Сообщение|false'
    )

    def to_data(self):
        fields = []
        for line in self.cleaned_data['fields_raw'].strip().splitlines():
            parts = line.split('|', 3)
            if len(parts) == 4:
                fields.append({
                    'name':     parts[0].strip(),
                    'type':     parts[1].strip(),
                    'label':    parts[2].strip(),
                    'required': parts[3].strip().lower() == 'true',
                })
        return {'fields': fields}


class FaqSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Вопросы и ответы (каждый с новой строки: вопрос|ответ)',
        widget=forms.Textarea,
        help_text='Пример: Как оставить заявку?|Заполните форму на сайте'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            if '|' in line:
                question, answer = line.split('|', 1)
                items.append({'question': question.strip(), 'answer': answer.strip()})
        return {'items': items}


class TestimonialsSectionForm(forms.Form):
    items_raw = forms.CharField(
        label='Отзывы (каждый с новой строки: имя|текст)',
        widget=forms.Textarea,
        help_text='Пример: Анна К.|Отличная работа, всё в срок!'
    )

    def to_data(self):
        items = []
        for line in self.cleaned_data['items_raw'].strip().splitlines():
            if '|' in line:
                name, text = line.split('|', 1)
                items.append({'name': name.strip(), 'text': text.strip()})
        return {'items': items}