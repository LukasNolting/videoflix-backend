import json
import time
from django.urls import reverse
from django.conf import settings
from django.views import View
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics
from videoflix_app.models import User, Video
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from videoflix_app.models import PasswordReset
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from videoflix_app.serializers import LoginSerializer, ResetPasswordRequestSerializer, UserSerializer
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib import messages
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import UserContinueWatchVideo, UserFavoriteVideo, Video
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from .serializers import VideoSerializer

User = get_user_model()

# CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)
# @cache_page(CACHETTL)

class VideoView(View):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        video_list = list(videos.values())
        return JsonResponse(video_list, safe=False)

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
            messages.success(request, 'Your account has been activated.')
        else:
            messages.info(request, 'Your account is already activated.')
        return redirect('http://localhost:4200/login')
    else:
        messages.error(request, 'The activation link is invalid!')
        return redirect('http://localhost:4200')

class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]
    TokenAuthentication = [AllowAny]
    User = get_user_model()
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
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

            reset_url = reverse('password_reset_token', kwargs={'token': token})
            relative_reset_url = reset_url.replace('/videoflix', '')
            custom_port_url = 'http://localhost:4200' + relative_reset_url
            full_url = custom_port_url
            print('full-Url' + full_url)
            subject = "Reset your password"
            text_content = render_to_string('emails/forgot_password.txt', {
                'username': user.username, 
                'full_url': full_url,
            })
            html_content = render_to_string('emails/forgot_password.html', {
                'username': user.username, 
                'full_url': full_url,
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

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def favorite_videos(request):
    if request.method == 'GET':
        favorite_videos = UserFavoriteVideo.objects.filter(user=request.user, is_favorite=True)
        videos = Video.objects.filter(id__in=[favorite.video.id for favorite in favorite_videos])
        video_list = list(videos.values())
        return JsonResponse(video_list, safe=False)
    
    elif request.method == 'POST':
        video_id = request.data.get('video_id')
        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = UserFavoriteVideo.objects.get_or_create(user=request.user, video=video)
        favorite.is_favorite = not favorite.is_favorite
        favorite.save()
        return Response({"is_favorite": favorite.is_favorite}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_continue_watching(request):
    if request.method == 'POST':
        video_id = request.data.get('video_id')
        timestamp = request.data.get('timestamp')
        
        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if timestamp is None:
            return Response({"error": "timestamp is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)
        
        continue_watch, created = UserContinueWatchVideo.objects.get_or_create(
            user=request.user, video=video,
            defaults={"timestamp": timestamp}
        )
        
        if not created:
            continue_watch.timestamp = timestamp
            continue_watch.save()
        
        return Response({"timestamp": continue_watch.timestamp}, status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        continue_watch_videos = UserContinueWatchVideo.objects.filter(user=request.user)
        video_ids = Video.objects.filter(id__in=[continue_watch.video.id for continue_watch in continue_watch_videos])
        videos = Video.objects.filter(id__in=video_ids)
        video_list = [
            {
                "video": {
                    "id": video.id,
                    "title": video.title,
                    "description": video.description,
                    "category": video.category,
                    "created_at": video.created_at,
                    "video_file": video.video_file.url.replace('/media/', '') if video.video_file else None,
                    "thumbnail": video.thumbnail.url.replace('/media/', '') if video.thumbnail else None,
                },
                "timestamp": next(
                    (cw.timestamp for cw in continue_watch_videos if cw.video_id == video.id), None
                )
            }
            for video in videos
        ]
        return JsonResponse(video_list, safe=False)
    
    elif request.method == 'DELETE':
        video_id = request.data.get('video_id')

        if not video_id:
            return Response({"error": "video_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            continue_watch = UserContinueWatchVideo.objects.get(user=request.user, video_id=video_id)
            continue_watch.delete()
            return Response({"message": "Video removed from continue watching."}, status=status.HTTP_204_NO_CONTENT)
        except UserContinueWatchVideo.DoesNotExist:
            return Response({"error": "Video not found in continue watching."}, status=status.HTTP_404_NOT_FOUND)


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