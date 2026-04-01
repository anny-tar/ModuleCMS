"""
Импортирует файлы из MEDIA_ROOT в медиабиблиотеку.

Использование:
    python manage.py import_media              # импортирует новые файлы
    python manage.py import_media --dry-run    # показывает что будет без записи в БД
    python manage.py import_media --cleanup    # удаляет записи у которых файла нет на диске
    python manage.py import_media --dry-run --cleanup  # показывает что будет удалено
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model


IMAGE_EXTS    = {'jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'}
VIDEO_EXTS    = {'mp4', 'webm', 'mov'}
SKIP_DIRS     = {'thumbnails', '.git', '__pycache__'}
SKIP_EXTS     = {'py', 'pyc', 'db', 'sqlite3', 'log'}


def detect_media_type(ext):
    if ext in IMAGE_EXTS:
        return 'image'
    if ext in VIDEO_EXTS:
        return 'video'
    return 'document'


class Command(BaseCommand):
    help = 'Импортирует файлы из MEDIA_ROOT в медиабиблиотеку и/или чистит битые записи'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано без реальных изменений в БД',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Удалить записи MediaFile у которых файл не существует на диске',
        )

    def handle(self, *args, **options):
        from media_library.models import MediaFile

        dry_run  = options['dry_run']
        cleanup  = options['cleanup']
        mode_tag = '[dry-run] ' if dry_run else ''

        if cleanup:
            self._cleanup(MediaFile, dry_run, mode_tag)
        else:
            self._import(MediaFile, dry_run, mode_tag)

    # ------------------------------------------------------------------
    # Импорт новых файлов
    # ------------------------------------------------------------------
    def _import(self, MediaFile, dry_run, mode_tag):
        media_root = settings.MEDIA_ROOT
        User       = get_user_model()
        superuser  = User.objects.filter(is_superuser=True).first()

        if not os.path.isdir(media_root):
            self.stderr.write(f'MEDIA_ROOT не найден: {media_root}')
            return

        existing = set(MediaFile.objects.values_list('file', flat=True))

        imported = skipped = errors = 0

        for dirpath, dirnames, filenames in os.walk(media_root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, media_root).replace('\\', '/')
                ext      = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

                if not ext or ext in SKIP_EXTS:
                    skipped += 1
                    continue

                if rel_path in existing:
                    skipped += 1
                    continue

                media_type = detect_media_type(ext)
                file_size  = os.path.getsize(abs_path)

                if dry_run:
                    self.stdout.write(f'  {mode_tag}{rel_path} ({media_type}, {file_size} байт)')
                    imported += 1
                    continue

                try:
                    obj               = MediaFile(
                        original_name = filename,
                        media_type    = media_type,
                        file_size     = file_size,
                        uploaded_by   = superuser,
                    )
                    obj.file.name = rel_path
                    obj.save()
                    imported += 1
                except Exception as e:
                    self.stderr.write(f'  Ошибка: {rel_path} — {e}')
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{mode_tag}Импорт: добавлено {imported}, пропущено {skipped}, ошибок {errors}'
        ))

    # ------------------------------------------------------------------
    # Очистка битых записей
    # ------------------------------------------------------------------
    def _cleanup(self, MediaFile, dry_run, mode_tag):
        media_root = settings.MEDIA_ROOT
        removed = not_found = 0

        for obj in MediaFile.objects.all():
            if not obj.file:
                continue
            abs_path = os.path.join(media_root, obj.file.name)
            if not os.path.isfile(abs_path):
                not_found += 1
                self.stdout.write(
                    f'  {mode_tag}Битая запись: [{obj.pk}] {obj.original_name} → {obj.file.name}'
                )
                if not dry_run:
                    obj.delete()
                    removed += 1

        if not_found == 0:
            self.stdout.write(self.style.SUCCESS('Битых записей не найдено.'))
        else:
            label = f'найдено {not_found}' if dry_run else f'удалено {removed} из {not_found}'
            self.stdout.write(self.style.SUCCESS(f'\n{mode_tag}Очистка: {label}'))