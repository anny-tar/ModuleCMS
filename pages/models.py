from django.db import models
from slugify import slugify


# Допустимые типы страниц
class PageType(models.TextChoices):
    DEFAULT  = 'default',   'Обычная страница'
    NEWS     = 'news_list', 'Новости'
    GALLERY  = 'gallery',   'Галерея'


class Page(models.Model):
    title        = models.CharField('Заголовок', max_length=200)
    slug         = models.SlugField('URL-адрес', max_length=200, unique=True, blank=True)
    page_type    = models.CharField('Тип страницы', max_length=20,
                                    choices=PageType.choices, default=PageType.DEFAULT)
    is_published = models.BooleanField('Опубликована', default=False)
    seo_title    = models.CharField('SEO заголовок', max_length=200, blank=True)
    seo_desc     = models.TextField('SEO описание', blank=True)
    order        = models.PositiveIntegerField('Порядок в меню', default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering            = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/{self.slug}/'


# Словарь эмодзи-иконок для каждого типа секции.
# Единственное место в проекте где они определяются —
# используется в admin, шаблонах и JS через data-атрибут.
SECTION_ICONS = {
    'hero':         '🖼️',
    'text':         '📝',
    'counters':     '🔢',
    'cards':        '🃏',
    'team':         '👥',
    'steps':        '👣',
    'table':        '📊',
    'chart':    '🥧',
    'form':         '📬',
    'faq':          '❓',
    'testimonials': '💬',
    'contacts':     '📍',
}


class Section(models.Model):

    class SectionType(models.TextChoices):
        HERO         = 'hero',         'Обложка (Hero)'
        TEXT         = 'text',         'Текстовый блок'
        COUNTERS     = 'counters',     'Счётчики / Достижения'
        CARDS        = 'cards',        'Карточки с преимуществами'
        TEAM         = 'team',         'Команда'
        STEPS        = 'steps',        'Этапы / Нумерованный список'
        TABLE        = 'table',        'Таблица'
        CHART    = 'chart',    'Диаграмма'
        FORM         = 'form',         'Форма обратной связи'
        FAQ          = 'faq',          'Вопросы и ответы'
        TESTIMONIALS = 'testimonials', 'Отзывы'
        CONTACTS     = 'contacts',     'Контактная информация'

    page       = models.ForeignKey(Page, on_delete=models.CASCADE,
                                   related_name='sections', verbose_name='Страница')
    type       = models.CharField('Тип секции', max_length=20,
                                  choices=SectionType.choices)
    title      = models.CharField('Заголовок секции', max_length=200, blank=True)
    order      = models.PositiveIntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Видима', default=True)
    data       = models.JSONField('Данные', default=dict, blank=True)
    draft_data = models.JSONField('Черновик', null=True, blank=True, default=None)

    class Meta:
        verbose_name        = 'Секция'
        verbose_name_plural = 'Секции'
        ordering            = ['order']

    def __str__(self):
        return f'{self.icon()} {self.get_type_display()} — {self.page.title}'

    def icon(self):
        """Возвращает эмодзи-иконку для типа секции."""
        return SECTION_ICONS.get(self.type, '📄')