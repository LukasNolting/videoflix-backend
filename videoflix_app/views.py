from django.shortcuts import render

# Create your views here.
from django.core.cache.backends.base import DEFAULT_TIMEOUT 
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

from videoflix_app.serializers import LoginSerializer, UserSerializer

class VideoView(View):
    def get(self, request, *args, **kwargs):
            
        videos = Video.objects.all()
        print(videos)
        # Deine Logik hier
        return JsonResponse({'message': 'Dies ist eine GET-Anfrage.'})

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
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib import messages

def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if not user.is_active:  # Überprüfen, ob der Benutzer bereits aktiviert ist
            user.is_active = True
            user.save()
            messages.success(request, 'Dein Konto wurde erfolgreich aktiviert!')
        else:
            messages.info(request, 'Dein Konto ist bereits aktiviert.')
        return redirect('login')
    else:
        messages.error(request, 'Der Aktivierungslink ist ungültig oder abgelaufen.')
        return redirect('home')
    