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

from videoflix_app.models import Video
# CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)


# @cache_page(CACHETTL)

from django.http import JsonResponse

from videoflix_app.serializers import LoginSerializer, UserSerializer

class VideoView(View):
    def get(self, request, *args, **kwargs):
        # Deine Logik hier
        return JsonResponse({'message': 'Dies ist eine GET-Anfrage.'})
    
    
# class LoginView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('email')
#         print(username)
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         print(user)
#         if user is not None:
#             token = self.get_or_create_token(user)
#             return Response({'token': token}, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

#     def get_or_create_token(self, user):
#         """
#         Gets or creates an authentication token for the user.

#         Args:
#             user (CustomUser): The user object for whom the token is generated.

#         Returns:
#             str: The authentication token for the user.
#         """
#         token, created = Token.objects.get_or_create(user=user)
#         return token.key



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