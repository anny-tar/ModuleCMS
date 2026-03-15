from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name  = models.CharField('Название', max_length=100)
    slug  = models.SlugField('URL', max_length=100, unique=True, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name        = 'Категория'
        verbose_name_plural = 'Категории новостей'
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Article(models.Model):
    title        = models.CharField('Заголовок', max_length=200)
    slug         = models.SlugField('URL', max_length=200, unique=True, blank=True)
    category     = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     verbose_name='Категория')
    cover        = models.ForeignKey('media_library.MediaFile',
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     verbose_name='Обложка')
    announce     = models.TextField('Анонс', blank=True)
    content      = models.TextField('Содержимое')
    is_published = models.BooleanField('Опубликована', default=False)
    published_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering            = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/news/{self.slug}/'