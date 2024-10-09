# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as token_generator
from .models import Video
import os
import logging
import django_rq

logger = logging.getLogger(__name__)



@receiver(post_save, sender=User)
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
            django_rq.enqueue(send_mail, subject, '', settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=message)
            logger.info(f'Aktivierungs-E-Mail zur Warteschlange hinzugefügt für {instance.email}')
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