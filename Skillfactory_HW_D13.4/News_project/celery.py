import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsProject.settings')

app = Celery('newsProject')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'weekly_newsletter': {
        'task': 'news_portal.tasks.newsletter_task',
        'schedule': crontab(day_of_week='monday', hour=8, minute=0),

    },
}