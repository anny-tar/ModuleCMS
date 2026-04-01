from django.db import models


class LeadSubmission(models.Model):
    section     = models.ForeignKey(
                      'pages.Section',
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      verbose_name='Секция формы'
                  )
    data        = models.JSONField('Данные заявки')
    ip_address  = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_viewed   = models.BooleanField('Просмотрена', default=False)

    class Meta:
        verbose_name        = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering            = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.pk} от {self.created_at.strftime("%d.%m.%Y %H:%M")}'