import django_filters
from django import forms
from .models import Post, Category

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Заголовок')
    postCategory = django_filters.ModelChoiceFilter(field_name='postCategory', queryset=Category.objects.all(), empty_label='Все', label='Категория', widget=forms.Select)
    date = django_filters.DateTimeFilter(field_name='dateCreation', lookup_expr='gte', label='Дата публикации (после)', widget=forms.DateTimeInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        fields = ['title', 'postCategory', 'date']