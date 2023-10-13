

from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Author, Category
from django.utils import timezone

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from django.core.mail import EmailMultiAlternatives

from django.core.mail import mail_admins



class PostForm(forms.ModelForm):
    postCategory = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Категория'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'postCategory']
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'postCategory': 'Категория',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.dateCreation = timezone.now()

        if commit:
            instance.save()
            self.save_m2m()  # Сохранение связей ManyToMany

        return instance

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")

        if text is not None and len(text) < 20:
            raise forms.ValidationError("Текст не может быть менее 20 символов.")

        title = cleaned_data.get("title")

        if title == text:
            raise forms.ValidationError("Текст не должен быть идентичным заголовку.")

        return cleaned_data



class CustomSignupForm(SignupForm):
   def save(self, request):
       user = super().save(request)
       author = Author.objects.create(authorUser=user, ratingAuthor=0)
       common_users = Group.objects.get(name="authors")
       user.groups.add(common_users)

       subject = 'Добро пожаловать в наш новостной портал!'
       text = f'{user.username}, вы успешно зарегистрировались на сайте!'
       html = (
            f'<b>{user.username}</b>, вы успешно зарегистрировались на '
            f'<a href="http://127.0.0.1:8000/Postnews">сайте</a>!'
        )
       msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
       msg.attach_alternative(html, "text/html")
       msg.send()

       mail_admins(
           subject=' Новый пользователь!',
           message=f'Пользователь {user.username} зарегистрировался на сайте.'
       )
       return user


