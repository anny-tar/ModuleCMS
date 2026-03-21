from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display        = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display        = ['title', 'category', 'is_published', 'published_at']
    list_filter         = ['is_published', 'category']
    search_fields       = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
