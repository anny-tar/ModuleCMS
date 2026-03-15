from django.urls import path
from . import views

urlpatterns = [
    path('gallery/',              views.gallery_list,   name='gallery_list'),
    path('gallery/<int:album_id>/', views.gallery_detail, name='gallery_detail'),
]