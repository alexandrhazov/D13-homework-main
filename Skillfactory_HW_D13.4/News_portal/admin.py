from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Author, Category, Post, Comment, PostCategory, Subscription

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'date_joined')

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('authorUser', 'ratingAuthor',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'dateCreation',)
    readonly_fields = ('dateCreation', 'postCategory')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('commentPost', 'commentUser', 'rating', 'dateCreation')
    readonly_fields = ('dateCreation',)

class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('postThrough', 'categoryThrough')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category']
    list_display_links = ['user', 'category']


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Subscription, SubscriptionAdmin)