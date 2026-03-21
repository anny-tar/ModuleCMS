from django.contrib import admin
from django.urls import reverse
from unfold.admin import ModelAdmin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    list_display = ['title', 'is_published']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['albums'] = Album.objects.all().order_by('order', '-created_at')
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            album = Album.objects.get(pk=object_id)
            photos = album.photos.order_by('order')
            photos_data = []
            for photo in photos:
                photos_data.append({
                    'id':         photo.pk,
                    'caption':    photo.caption or '(без подписи)',
                    'thumb':      photo.file.file.url if photo.file and photo.file.file else None,
                    'edit_url':   reverse('admin:gallery_photo_change', args=[photo.pk]),
                    'delete_url': reverse('admin:gallery_photo_delete', args=[photo.pk]),
                })
            extra_context['photos_data']   = photos_data
            extra_context['add_photo_url'] = (
                reverse('admin:gallery_photo_add') + f'?album={object_id}'
            )
        except Album.DoesNotExist:
            pass
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Photo)
class PhotoAdmin(ModelAdmin):
    list_display  = ['__str__', 'album']
    list_filter   = ['album']
    exclude       = ['order']

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        album_id = request.GET.get('album')
        if album_id:
            initial['album'] = album_id
        return initial

    def save_model(self, request, obj, form, change):
        if not change and obj.album_id:
            from django.db.models import Max
            max_order = Photo.objects.filter(album=obj.album).aggregate(m=Max('order'))['m']
            obj.order = (max_order + 1) if max_order is not None else 0
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        from django.http import HttpResponseRedirect
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return HttpResponseRedirect(
                reverse('admin:gallery_album_change', args=[obj.album_id])
            )
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        from django.http import HttpResponseRedirect
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return HttpResponseRedirect(
                reverse('admin:gallery_album_change', args=[obj.album_id])
            )
        return super().response_add(request, obj, post_url_continue)