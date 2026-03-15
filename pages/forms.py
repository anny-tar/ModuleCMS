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