from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'order']
    list_editable       = ['order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display        = ['title', 'category', 'is_published', 'published_at']
    list_editable       = ['is_published']
    list_filter         = ['is_published', 'category']
    search_fields       = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}