from django.shortcuts import render

# Create your views here.
from django.core.cache.backends.base import DEFAULT_TIMEOUT 
from django.urls import reverse
from django.views.decorators.cache import cache_page 
from django.conf import settings
from rest_framework.response import Response
from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework import generics

from videoflix_app.models import User, Video
# CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)


# @cache_page(CACHETTL)

from django.http import JsonResponse

from videoflix_app.serializers import LoginSerializer, ResetPasswordRequestSerializer, UserSerializer

class VideoView(View):
    def get(self, request, *args, **kwargs):
            
        videos = Video.objects.all()
        video_list = list(videos.values())
        return JsonResponse(video_list, safe=False)

class LoginView(APIView):
    """
    API view for user login.

    This view handles user authentication by validating login credentials
    and returning a token if authentication is successful.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user login.

        Parameters:
        
request: HTTP request containing login data.

        Returns:
        
Response: JSON response with token on success or error messages on failure."""
        serializer = LoginSerializer(data=request.data)
        # print(serializer.is_valid)
        if serializer.is_valid(raise_exception=True):
          user = serializer.validated_data['user']
          token, created = Token.objects.get_or_create(user=user)
          return Response({'token': token.key}, status=status.HTTP_200_OK)   # todo if create user then create reponding contact})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """
    View for creating a new user.

    Inherits from `CreateAPIView` and uses the `UserSerializer` to validate and create a new user.
    """
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib import messages

# Verwende das benutzerdefinierte User-Modell
User = get_user_model()

def activate_user(request, uidb64, token):
    try:
        
        uid = urlsafe_base64_decode(uidb64).decode()
        
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    
    if user is not None and token_generator.check_token(user, token):
        if not user.is_active: 
            user.is_active = True
            user.save()
            messages.success(request, 'Dein Konto wurde erfolgreich aktiviert!')
        else:
            messages.info(request, 'Dein Konto ist bereits aktiviert.')
        return redirect('http://localhost:4200/login')
    else:
        messages.error(request, 'Der Aktivierungslink ist ungültig oder abgelaufen.')
        return redirect('http://localhost:4200')
    
    
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from videoflix_app.models import PasswordReset
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]
    User = get_user_model()
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        print(email)
        user = User.objects.filter(email__iexact=email).first()
        print(user)

        if user:
            token_generator = PasswordResetTokenGenerator()
            print('Token-Generator' + f'{token_generator}')
            token = token_generator.make_token(user) 
            print('Token' + f'{token}')
            reset = PasswordReset(email=email, token=token)
            print('reset' + f'{reset}')
            reset.save()

            reset_url = reverse('password-reset-token', kwargs={'token': token})
            relative_reset_url = reset_url.replace('/videoflix', '')
            custom_port_url = 'http://localhost:4200' + relative_reset_url
            full_url = custom_port_url
            print('full-Url' + full_url)


            subject = "Passwort zurücksetzen"
            text_content = render_to_string('emails/forgot_password.txt', {
                'username': user.username,  # Korrektur hier
                'full_url': full_url,
            })
            html_content = render_to_string('emails/forgot_password.html', {
                'username': user.username,  # Korrektur hier
                'full_url': full_url,
            })
            print('html' + html_content)

            # # Erstelle die E-Mail
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return Response({'success': 'Wir haben Ihnen einen Link zur Zurücksetzung Ihres Passworts gesendet'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Benutzer mit diesen Anmeldeinformationen nicht gefunden"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class PasswordResetView(generics.GenericAPIView):
    permission_classes = []

    def post(self, request, token):
        User = get_user_model()
        
        # Filtere das PasswordReset Model nach dem Token
        reset_obj = PasswordReset.objects.filter(token=token).first()
        print(f'reset_obj {reset_obj}')
        
        if not reset_obj:
            return Response({'error': 'Invalid token'}, status=400)
        
        # Suche den User basierend auf der Email in reset_obj
        user = User.objects.filter(email=reset_obj.email).first()
        
        if user:
            # Setze das neue Passwort
            user.set_password(request.data['password'])
            user.save()
            
            # Lösche den Reset-Token-Eintrag nach erfolgreichem Passwort-Reset
            reset_obj.delete()
            
            return Response({'success': 'Password updated'})
        else: 
            return Response({'error': 'No user found'}, status=404)
