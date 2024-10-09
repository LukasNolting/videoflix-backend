# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as token_generator

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
