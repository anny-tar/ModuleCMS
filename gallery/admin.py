from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model  = Photo
    extra  = 0
    fields = ['file', 'caption']


@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    list_display = ['title', 'is_published']
    inlines      = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(ModelAdmin):
    list_display = ['__str__', 'album']
    list_filter  = ['album']
