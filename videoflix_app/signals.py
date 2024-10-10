# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as token_generator
from .models import Video, User
import os
from videoflix_app.tasks import convert_video
import logging
from django.core.mail import EmailMultiAlternatives
import django_rq

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_activation_email_v2(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        # First, render the plain text content.
        print(instance)
        token = token_generator.make_token(instance)
        print(token)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        print(uid)
        activation_url = reverse('activate_user', kwargs={'uidb64': uid, 'token': token})
        print(activation_url)
        full_url = f'{settings.DOMAIN_NAME}{activation_url}'
        print
        
        text_content = render_to_string(
            "templates/emails/activation_email.txt",
            context={
                'user': instance,
                'activation_url': full_url,
            },
        )

        # Secondly, render the HTML content.
        html_content = render_to_string(
            "templates/emails/activation_email.html",
            context={
                'user': instance,
                'activation_url': full_url,
            },
        )
        
        subject = 'Aktiviere dein Konto'

        # Then, create a multipart email instance.
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            # headers={"List-Unsubscribe": "<mailto:unsub@example.com>"},
        )
        print(msg)

        # Lastly, attach the HTML content to the email instance and send.
        msg.attach_alternative(html_content, "text/html")
        msg.send()



# @receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        logger.info(f'Creating activation email for {instance.email}')
        try:
            token = token_generator.make_token(instance)
            uid = urlsafe_base64_encode(force_bytes(instance.pk))
            activation_url = reverse('activate_user', kwargs={'uidb64': uid, 'token': token})
            full_url = f'{settings.DOMAIN_NAME}{activation_url}'

            # E-Mail versenden
            subject = 'Aktiviere dein Konto'
            message = render_to_string('activation_email.html', {
                'user': instance,
                'activation_url': full_url,
            })


            # Füge die Aufgabe zur Warteschlange hinzu
            # django_rq.enqueue(send_mail, subject, '', settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=message)
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=message, fail_silently=False)
            # logger.info(f'Aktivierungs-E-Mail zur Warteschlange hinzugefügt für {instance.email}')
        except Exception as e:
            logger.error(f'Fehler beim Senden der E-Mail: {e}')

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver for post_save on Video model.

    This method is connected to the post_save signal of the Video model.
    When a new Video is created, this method is called. It prints a message
    to the console for debugging purposes.

    Parameters
    ----------
    sender : Model class
        The model class that sent the signal.
    instance : Model instance
        The actual instance of the model that was created.
    created : bool
        A boolean indicating whether a new record was created.
    **kwargs
        Additional keyword arguments.
    """
    print('Video was created')
    if created:
        print('new Video was created')
        convert_video(instance.video_file.path)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Deletes the video file from the file system after it has been
    deleted in the database.

    This receiver is connected to the post_delete signal of the Video
    model. It first checks if the video_file attribute of the instance
    is not empty and if the file exists in the file system. If both
    conditions are true, it deletes the file from the file system.

    :param sender: The sender of the signal, usually the Video model
    :param instance: The instance of the Video model that was deleted
    :param kwargs: Additional keyword arguments
    """
    print('Video will be deleted')
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print('Video was deleted')