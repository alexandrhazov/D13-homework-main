from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .tasks import send_notifications_task
from .models import *



#def send_notifications(preview, pk, title, subscribers_emails):
#    html_content = render_to_string(
#        'flatpages/post_created_email_signal.html',
#        {
#            'text': preview,
#            'link': f'http://127.0.0.1:8000/Postnews/{pk}',
#        }
#    )
#
#    msg = EmailMultiAlternatives(
#        subject=title,
#        body='',
#        from_email=settings.DEFAULT_FROM_EMAIL,
#        to=subscribers_emails
#    )
#
#    msg.attach_alternative(html_content, "text/html")
#    msg.send()


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        subscribers_emails = []

        for cat in categories:
            subscribers = Subscription.objects.filter(category=cat)
            subscribers_emails += [subs.user.email for subs in subscribers]
            #print(subscribers_emails)

        send_notifications_task.apply_async(args=(instance.preview(), instance.pk, instance.title, subscribers_emails))