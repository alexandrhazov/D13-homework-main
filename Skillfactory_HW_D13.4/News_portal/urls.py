import os
from django.urls import path
# Импортируем созданное нами представление
from .views import NewsListView, NewsDetailView, NewsSearchView, PostCreateView, NewsUpdateView, NewsDeleteView,  ArticleUpdateView, ArticleDeleteView, subscriptions




urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('<int:pk>', NewsDetailView.as_view(), name='news_detail'),

    path('search/', NewsSearchView.as_view(), name='news_search'),
    path('news/create/', PostCreateView.as_view(), name='post_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('articles/create/', PostCreateView.as_view(), name='post_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('subscriptions/', subscriptions, name='subscriptions'),

    # остальные URL-шаблоны вашего проекта
]