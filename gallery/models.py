from django.db import models


class Album(models.Model):
    title        = models.CharField('Название', max_length=200)
    description  = models.TextField('Описание', blank=True)
    cover        = models.ForeignKey('media_library.MediaFile',
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='album_cover',
                                     verbose_name='Обложка альбома')
    order        = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубликован', default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Альбом'
        verbose_name_plural = 'Альбомы'
        ordering            = ['order', '-created_at']

    def __str__(self):
        return self.title


class Photo(models.Model):
    album   = models.ForeignKey(Album, on_delete=models.CASCADE,
                                related_name='photos', verbose_name='Альбом')
    file    = models.ForeignKey('media_library.MediaFile',
                                on_delete=models.CASCADE,
                                verbose_name='Файл')
    caption = models.CharField('Подпись', max_length=200, blank=True)
    order   = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name        = 'Фото'
        verbose_name_plural = 'Фотографии'
        ordering            = ['order']

    def __str__(self):
        return f'{self.album.title} — {self.order}'