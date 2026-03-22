from django.urls import path
from . import views

urlpatterns = [
    # AJAX: сортировка
    path('pages/section/sort/', views.section_sort, name='section_sort'),
    path('pages/sort/', views.page_sort, name='page_sort'),
    # Публичные страницы — обязательно последний паттерн
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]