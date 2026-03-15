from django.shortcuts import get_object_or_404, render
from .models import Article, Category


def news_list(request):
    articles   = Article.objects.filter(is_published=True)
    categories = Category.objects.all()
    # Фильтрация по категории если передан параметр
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    return render(request, 'news/news_list.html', {
        'articles':   articles,
        'categories': categories,
    })


def news_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'news/news_detail.html', {'article': article})