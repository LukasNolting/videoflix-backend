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


from videoflix_app.models import Video
from videoflix_app.serializers import VideoSerializer
# CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)


# @cache_page(CACHETTL)

from django.http import JsonResponse

class VideoView(View):
    def get(self, request, *args, **kwargs):
        # Deine Logik hier
        return JsonResponse({'message': 'Dies ist eine GET-Anfrage.'})
