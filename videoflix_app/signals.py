import os
from dotenv import load_dotenv
import logging
import shutil
import threading

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth import get_user_model, tokens
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.files.base import ContentFile

from django_rq import job, get_queue

from rest_framework.authtoken.models import Token

from videoflix_app.tasks import process_video
from .models import Video


load_dotenv()

logger = logging.getLogger(__name__)
User = get_user_model() 

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal receiver to create a new Token for a User instance when
    one is created. This is the default behavior of the
    rest_framework.authtoken app when running the
    `createauthtoken` management command.

    Args:
        sender (User): The User model class
        instance (User): The User instance being saved
        created (bool): Whether the instance is being created
            (True) or updated (False)
    """
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=User) 
def send_activation_email_v2(sender, instance, created, **kwargs):
    """
    Signal receiver to send an activation email to a User instance when
    one is created and not yet activated.

    Args:
        sender (User): The User model class
        instance (User): The User instance being saved
        created (bool): Whether the instance is being created (True) or updated (False)
    """
    if created and not instance.is_active:
        token = token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_url = reverse('activate_user', kwargs={'uidb64': uid, 'token': token})
        full_url = f'{settings.DOMAIN_NAME}{activation_url}'
        domain_url = os.getenv('REDIRECT_LANDING')
        text_content = render_to_string(
            "emails/activation_email.txt",
            context={'user': instance, 'activation_url': full_url, 'domain_url': domain_url},
        )
        html_content = render_to_string(
            "emails/activation_email.html",
            context={'user': instance, 'activation_url': full_url, 'domain_url': domain_url},
        )
        subject = 'Confirm your email'
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver to enqueue the video processing task when a Video instance is
    created.

    Args:
        sender (Video): The Video model class
        instance (Video): The Video instance being saved
        created (bool): Whether the instance is being created (True) or updated (False)
        **kwargs: Additional keyword arguments
    """
    if created:
        queue = get_queue('default')
        queue.enqueue(process_video, instance)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal receiver to delete the video file folder when a Video instance is deleted.

    Args:
        sender (Video): The Video model class
        instance (Video): The Video instance being deleted
        **kwargs: Additional keyword arguments
    """
    folder_path = os.path.dirname(instance.video_file.path)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)