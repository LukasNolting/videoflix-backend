import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setze die Umgebungsvariable für Django-Einstellungen
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videoflix.settings')  # Ersetze 'videoflix.settings' mit deinem tatsächlichen Settings-Modul

# Initialisiere Django
django.setup()

def test_email():
    subject = 'Test E-Mail'
    message = 'Dies ist eine Test-E-Mail, um die SMTP-Konfiguration zu prüfen.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['noreply@lukas-nolting.de']  # Setze hier eine gültige Empfängeradresse ein

    try:
        send_mail(subject, message, from_email, recipient_list)
        print("E-Mail wurde erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

# Test E-Mail senden
test_email()
