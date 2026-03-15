from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model  = Photo
    extra  = 0
    fields = ['file', 'caption', 'order']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display  = ['title', 'is_published', 'order']
    list_editable = ['is_published', 'order']
    inlines       = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'album', 'order']
    list_filter   = ['album']
    list_editable = ['order']