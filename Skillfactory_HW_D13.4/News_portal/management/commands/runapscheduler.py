import html
import logging
from django.core.mail import send_mail
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings

from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.utils import timezone
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from news_portal.models import Post, Subscription

logger = logging.getLogger(__name__)

# мой планировщик

def my_job():
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


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger = CronTrigger(day_of_week="fri", hour="18", minute="00"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
