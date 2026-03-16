from django.urls import path
from . import views

urlpatterns = [
    path('pages/section/sort/', views.section_sort, name='section_sort'),
    path('pages/sort/', views.page_sort, name='page_sort'),
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]