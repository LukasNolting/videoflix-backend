from datetime import timedelta
from django.utils import timezone, http
from django.urls import reverse
from django.conf import settings
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, tokens
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator as token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_decode
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from videoflix_app.models import User, Video, PasswordReset, UserContinueWatchVideo, UserFavoriteVideo
from videoflix_app.serializers import LoginSerializer, ResetPasswordRequestSerializer, UserSerializer
import os
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()

class VideoView(View):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cached_videos = cache.get('all_videos')
        if cached_videos is None:
            videos = Video.objects.all()
            cached_videos = list(videos.values())
            cache.set('all_videos', cached_videos, timeout=60*15)
        return JsonResponse(cached_videos, safe=False)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
          user = serializer.validated_data['user']
          token, created = Token.objects.get_or_create(user=user)
          return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]
    TokenAuthentication = [AllowAny]
    User = get_user_model()
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        email = request.data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user) 
            reset = PasswordReset(email=email, token=token)
            reset.save()

            reset_url = reverse('password_reset_token', kwargs={'token': token})
            relative_reset_url = reset_url.replace('/videoflix', '')
            custom_port_url = os.getenv('DOMAIN_NAME') + relative_reset_url
            full_url = custom_port_url
            domain_url = os.getenv('REDIRECT_LANDING')
            subject = "Reset your password"
            text_content = render_to_string('emails/forgot_password.txt', {
                'username': user.username, 
                'full_url': full_url,
                'domain_url': domain_url,
            })
            html_content = render_to_string('emails/forgot_password.html', {
                'username': user.username, 
                'full_url': full_url,
                'domain_url': domain_url,
            })
            print('html' + html_content)
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class PasswordResetView(APIView):
    permission_classes = []

    def get(self, request, token):
        reset_obj = PasswordReset.objects.filter(token=token).first()
        if not reset_obj:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        token_lifetime = timedelta(hours=24)
        print(token_lifetime)
        if timezone.now() > reset_obj.created_at + token_lifetime:
            return Response({'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Token is valid'}, status=status.HTTP_200_OK)

    def post(self, request, token):
        reset_obj = PasswordReset.objects.filter(token=token).first()
        if not reset_obj:
            return Response({'error': 'Invalid token'}, status=400)

        token_lifetime = timedelta(hours=24)
        if timezone.now() > reset_obj.created_at + token_lifetime:
            return Response({'error': 'Token expired'}, status=400)

        user = User.objects.filter(email=reset_obj.email).first()
        if user:
            user.set_password(request.data['password'])
            user.save()
            reset_obj.delete()
            return Response({'success': 'Password updated'})
        else:
            return Response({'error': 'No user found'}, status=404)

class VerifyTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        frontend_token = request.data.get('token')
        user_token = request.auth
        
        if frontend_token == str(user_token):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)