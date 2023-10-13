import os
from pathlib import Path

from django.utils import timezone
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from .models import Post, Category, Subscription
from datetime import datetime

from .forms import PostForm
from .filters import PostFilter
from django.urls import reverse_lazy
from django.urls import reverse
from django.shortcuts import redirect



from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Subquery, DateTimeField
from django.views.decorators.csrf import csrf_protect

import logging

logger = logging.getLogger(__name__)

class NewsListView(ListView):
    logger.error('Произошла ошибка', exc_info=True)
    model = Post
    queryset = Post.objects.filter().order_by('-dateCreation')
    template_name = 'news_list.html'
    context_object_name = 'post_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # К словарю добавим текущую дату в ключ 'time_now'.
        context['time_now'] = timezone.localtime(timezone.now())
        return context



class NewsDetailView(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'post'



class NewsSearchView(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news'
    paginate_by = 3

    def get_queryset(self):
        filter_form = PostFilter(self.request.GET, queryset=super().get_queryset())
        news = filter_form.qs

        selected_date = self.request.GET.get('date')
        selected_time = self.request.GET.get('time')

        if selected_date and selected_time:
            datetime_str = f'{selected_date} {selected_time}'
            selected_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            news = news.filter(dateCreation__gte=selected_datetime)

        selected_category = self.request.GET.get('postCategory')

        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = PostFilter(self.request.GET, queryset=self.get_queryset())
        categories = Category.objects.all()
        selected_category = self.request.GET.get('postCategory')
        context['filter_form'] = filter_form
        context['categories'] = categories
        context['selected_category'] = selected_category
        return context



class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_create.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/Postnews/news/create/':
            post.categoryType = Post.NEWS
        post.author = self.request.user.author
        post.save()
        return super().form_valid(form)


# Представление для редактирования новости
class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'


    def get_success_url(self):
        return reverse('news_detail', args=[self.object.pk])

# Представление для удаления новости
class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal.delete_post',)
    model = Post
    template_name = 'news_delete.html'
    success_url = '/Postnews/'  # URL для перенаправления после успешного удаления

# Представление для редактирования статьи
class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'


    def get_success_url(self):
        return reverse('news_detail', args=[self.object.pk])

# Представление для удаления статьи
class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal.delete_post',)
    model = Post
    template_name = 'article_delete.html'
    success_url = '/Postnews/'



@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        ),
        latest_post_title=Subquery(
            Post.objects.filter(
                postcategory__categoryThrough=OuterRef('pk')
            ).order_by('-dateCreation')[:1].values('title')
        ),
        author_name=Subquery(
            Post.objects.filter(
                postcategory__categoryThrough=OuterRef('pk')
            ).order_by('-dateCreation')[:1].values('author__authorUser__username')
        ),
        category_type=Subquery(
            Post.objects.filter(
                postcategory__categoryThrough=OuterRef('pk')
            ).order_by('-dateCreation')[:1].values('categoryType')
        ),
    ).order_by('name')

    return render(
        request,
        'subscriptions.html',
        {'categories_with': categories_with},
    )


