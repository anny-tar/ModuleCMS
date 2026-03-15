from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MediaFile(models.Model):

    class MediaType(models.TextChoices):
        IMAGE    = 'image',    'Изображение'
        VIDEO    = 'video',    'Видео'
        DOCUMENT = 'document', 'Документ'

    file          = models.FileField('Файл', upload_to='uploads/%Y/%m/')
    media_type    = models.CharField('Тип', max_length=20,
                                     choices=MediaType.choices, default=MediaType.IMAGE)
    original_name = models.CharField('Оригинальное имя', max_length=255)
    alt_text      = models.CharField('Alt-текст', max_length=255, blank=True)
    uploaded_by   = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      null=True, verbose_name='Загрузил')
    uploaded_at   = models.DateTimeField(auto_now_add=True)
    file_size     = models.PositiveIntegerField('Размер (байт)', default=0)

    class Meta:
        verbose_name        = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'
        ordering            = ['-uploaded_at']

    def __str__(self):
        return self.original_name

    def save(self, *args, **kwargs):
        # Сохранение оригинального имени файла при загрузке
        if not self.original_name and self.file:
            self.original_name = self.file.name
        # Автоопределение типа по расширению
        if self.file:
            ext = self.file.name.rsplit('.', 1)[-1].lower()
            if ext in ('jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'):
                self.media_type = self.MediaType.IMAGE
            elif ext in ('mp4', 'webm', 'mov'):
                self.media_type = self.MediaType.VIDEO
            else:
                self.media_type = self.MediaType.DOCUMENT
        super().save(*args, **kwargs)
        # Запись размера файла после сохранения
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
                MediaFile.objects.filter(pk=self.pk).update(file_size=self.file_size)
            except Exception:
                pass

    @property
    def url(self):
        return self.file.url if self.file else ''

    @property
    def is_image(self):
        return self.media_type == self.MediaType.IMAGE