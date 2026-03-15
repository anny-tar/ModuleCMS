from django.urls import path
from . import views

urlpatterns = [
    # Динамический маршрут — slug любой опубликованной страницы
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]