from django.db import models


class Theme(models.Model):
    name       = models.CharField('Название', max_length=100)
    is_custom  = models.BooleanField('Пользовательская', default=False)
    primary    = models.CharField('Primary (кнопки, акценты)', max_length=7, default='#2563eb')
    background = models.CharField('Background (фон страницы)', max_length=7, default='#ffffff')
    surface    = models.CharField('Surface (фон карточек)',    max_length=7, default='#f8fafc')
    accent     = models.CharField('Accent (hover-эффекты)',    max_length=7, default='#1d4ed8')
    text       = models.CharField('Text (основной текст)',     max_length=7, default='#1e293b')

    class Meta:
        verbose_name        = 'Тема оформления'
        verbose_name_plural = 'Темы оформления'

    def __str__(self):
        return self.name


class Font(models.Model):
    name             = models.CharField('Название', max_length=100)
    is_custom        = models.BooleanField('Загруженный шрифт', default=False)
    google_font_name = models.CharField('Название в Google Fonts', max_length=100, blank=True)
    fallback         = models.CharField('Запасной шрифт', max_length=100,
                                        default='sans-serif')
    custom_file      = models.ForeignKey('media_library.MediaFile',
                                         on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         verbose_name='Файл шрифта (.woff2)')

    class Meta:
        verbose_name        = 'Шрифт'
        verbose_name_plural = 'Шрифты'

    def __str__(self):
        return self.name


class SiteSettings(models.Model):

    class NavMode(models.TextChoices):
        LOGO_AND_NAME = 'logo_and_name', 'Логотип и название'
        LOGO_ONLY     = 'logo_only',     'Только логотип'
        NAME_ONLY     = 'name_only',     'Только название'
        HIDDEN        = 'hidden',        'Скрыть'

    site_name    = models.CharField('Название сайта', max_length=200, default='Мой сайт')
    active_theme = models.ForeignKey(Theme, on_delete=models.SET_NULL,
                                     null=True, blank=True, verbose_name='Активная тема')
    active_font  = models.ForeignKey(Font, on_delete=models.SET_NULL,
                                     null=True, blank=True, verbose_name='Активный шрифт')

    # Логотип и фавикон через медиабиблиотеку
    logo    = models.ForeignKey('media_library.MediaFile',
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='logo_settings',
                                verbose_name='Логотип')
    favicon = models.ForeignKey('media_library.MediaFile',
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='favicon_settings',
                                verbose_name='Фавикон (.ico или .png)')

    # Режим отображения логотипа/названия в навигации
    nav_mode = models.CharField('Навигация: логотип и название',
                                max_length=20,
                                choices=NavMode.choices,
                                default=NavMode.NAME_ONLY)

    # Контактные данные
    contact_address = models.TextField('Адрес', blank=True)
    contact_phone   = models.CharField('Телефон', max_length=100, blank=True)
    contact_email   = models.EmailField('Email', blank=True)
    contact_hours   = models.CharField('Режим работы', max_length=200, blank=True)
    contact_map_url = models.URLField('Ссылка на карту (embed)', max_length=500, blank=True)

    class Meta:
        verbose_name        = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj