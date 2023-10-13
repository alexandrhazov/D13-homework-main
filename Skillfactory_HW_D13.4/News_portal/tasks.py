from celery import shared_task
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.utils import timezone
from datetime import timedelta



from .models import *

@shared_task
def send_notifications_task(preview, pk, title, subscribers_emails):
    html_content = render_to_string(
        'flatpages/post_created_email_signal.html',
        {
            'text': preview,
            'link': f'http://127.0.0.1:8000/Postnews/{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def newsletter_task():
    # Получение последних новостей и подписчиков
    subscriptions = Subscription.objects.select_related('category', 'user')
    for subscription in subscriptions:
        category_name = subscription.category.name
        user = subscription.user
        user_email = user.email

        last_notification_date = timezone.now() - timedelta(days=7)

        new_posts = set(Post.objects.filter(dateCreation__gt=last_notification_date, postCategory__name=category_name))

        articles = []

        for article in new_posts:
            preview = article.preview()
            pk = article.pk
            title = article.title

            articles.append({
                'text': preview,
                'link': f"http://127.0.0.1:8000/Postnews/{pk}",
            })

        html_content = render_to_string(
            'flatpages/post_created_email.html',
            {
                'articles': articles,
            }
        )
        msg = EmailMultiAlternatives(
            subject=title,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email]
        )

        #вывод в терминал
        #print(f"Subject: {title}")
        #print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        #print(f"To: {user_email}")
        #print(f"HTML Content:\n{html_content}")
        #print("")

        msg.attach_alternative(html_content, "text/html")
        msg.send()


