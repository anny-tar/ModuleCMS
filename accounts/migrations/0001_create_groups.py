from django.db import migrations


# Права доступа для каждой группы
GROUP_PERMISSIONS = {
    'Контент-редактор': [
        'pages.add_page',    'pages.change_page',    'pages.view_page',
        'pages.add_section', 'pages.change_section', 'pages.view_section',
        'news.add_article',  'news.change_article',  'news.view_article',
        'news.add_category', 'news.change_category', 'news.view_category',
        'gallery.add_album', 'gallery.change_album', 'gallery.view_album',
        'gallery.add_photo', 'gallery.change_photo', 'gallery.view_photo',
        'media_library.add_mediafile',
        'media_library.change_mediafile',
        'media_library.view_mediafile',
    ],
    'Менеджер': [
        'leads.view_leadsubmission',
        'leads.change_leadsubmission',
    ],
    'SMM': [
        'news.add_article',  'news.change_article',  'news.view_article',
        'news.add_category', 'news.change_category', 'news.view_category',
        'media_library.add_mediafile',
        'media_library.view_mediafile',
    ],
}


def create_groups(apps, schema_editor):
    Group      = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.clear()

        for codename_full in perm_codenames:
            app_label, codename = codename_full.split('.')
            try:
                perm = Permission.objects.get(
                    codename=codename,
                    content_type__app_label=app_label
                )
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                # Пропуск если право ещё не создано
                pass


def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=GROUP_PERMISSIONS.keys()).delete()


class Migration(migrations.Migration):

    # Зависимость от миграций всех приложений с нужными правами
    dependencies = [
        ('auth',          '0012_alter_user_first_name_max_length'),
        ('pages',         '0002_alter_section_type'),
        ('news',          '0001_initial'),
        ('gallery',       '0001_initial'),
        ('leads',         '0001_initial'),
        ('media_library', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]