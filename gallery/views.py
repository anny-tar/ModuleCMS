from django.shortcuts import get_object_or_404, render
from .models import Album


def gallery_list(request):
    albums = Album.objects.filter(is_published=True)
    return render(request, 'gallery/gallery_list.html', {'albums': albums})


def gallery_detail(request, album_id):
    album  = get_object_or_404(Album, pk=album_id, is_published=True)
    photos = album.photos.select_related('file').all()
    return render(request, 'gallery/gallery_detail.html', {
        'album':  album,
        'photos': photos,
    })