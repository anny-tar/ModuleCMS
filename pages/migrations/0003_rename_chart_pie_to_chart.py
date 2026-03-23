from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_alter_section_type'),
    ]

    operations = [
        # Переименовываем значения в существующих записях
        migrations.RunSQL(
            sql="UPDATE pages_section SET type = 'chart' WHERE type = 'chart_pie';",
            reverse_sql="UPDATE pages_section SET type = 'chart_pie' WHERE type = 'chart';",
        ),
        # Обновляем choices
        migrations.AlterField(
            model_name='section',
            name='type',
            field=models.CharField(
                choices=[
                    ('hero',         'Обложка (Hero)'),
                    ('text',         'Текстовый блок'),
                    ('counters',     'Счётчики / Достижения'),
                    ('cards',        'Карточки с преимуществами'),
                    ('team',         'Команда'),
                    ('steps',        'Этапы / Нумерованный список'),
                    ('table',        'Таблица'),
                    ('chart',        'Диаграмма'),
                    ('form',         'Форма обратной связи'),
                    ('faq',          'Вопросы и ответы'),
                    ('testimonials', 'Отзывы'),
                    ('contacts',     'Контактная информация'),
                ],
                max_length=20,
                verbose_name='Тип секции',
            ),
        ),
    ]