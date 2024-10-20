from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth import get_user_model 
import os
from videoflix_app.tasks import process_video
import logging
from django.core.mail import EmailMultiAlternatives
import django_rq
from django.core.files.base import ContentFile
import threading
import logging
from .models import Video
from rest_framework.authtoken.models import Token
import shutil



logger = logging.getLogger(__name__)
User = get_user_model() 

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=User) 
def send_activation_email_v2(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_url = reverse('activate_user', kwargs={'uidb64': uid, 'token': token})
        full_url = f'{settings.DOMAIN_NAME}{activation_url}'
        text_content = render_to_string(
            "emails/activation_email.txt",
            context={'user': instance, 'activation_url': full_url},
        )
        html_content = render_to_string(
            "emails/activation_email.html",
            context={'user': instance, 'activation_url': full_url},
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
    Starts a new thread to convert and create a thumbnail for a video when it is saved for the first time.

    This receiver is connected to the post_save signal of the Video model. When a new video is saved, it starts a new
    thread which calls the process_video_and_thumbnail function with the instance of the video as argument.

    :param sender: The sender of the signal, usually the Video model
    :param instance: The instance of the Video model that was saved
    :param created: A boolean indicating whether the instance was created or updated
    :param kwargs: Additional keyword arguments
    """
    print('Video received')
    if created:
        thread = threading.Thread(target=process_video, args=(instance,))
        thread.start()
        # RQ-Worker anstatt thread
        

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    print('Video will be deleted')
    folder_path = os.path.dirname(instance.video_file.path)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f'Folder {folder_path} was deleted')

