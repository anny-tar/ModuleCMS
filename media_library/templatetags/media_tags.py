from django import template
from media_library.models import MediaFile

register = template.Library()


@register.simple_tag
def get_media(image_id):
    # Возвращает объект MediaFile по ID или None
    if not image_id:
        return None
    try:
        return MediaFile.objects.get(pk=image_id)
    except MediaFile.DoesNotExist:
        return None