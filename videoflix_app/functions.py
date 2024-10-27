from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from videoflix_app.models import User, Video, UserContinueWatchVideo, UserFavoriteVideo
import os

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
        return redirect(os.getenv('REDIRECT_LOGIN'))
    else:
        messages.error(request, 'The activation link is invalid!')
        return redirect(os.getenv('REDIRECT_LANDING'))
       
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