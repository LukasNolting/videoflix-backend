from django.shortcuts import render

# Create your views here.
from django.core.cache.backends.base import DEFAULT_TIMEOUT 
from django.views.decorators.cache import cache_page 
from django.conf import settings
CACHETTL = getattr(settings, 'CACHETTL', DEFAULT_TIMEOUT)


@cache_page(CACHETTL)
def test():
    print("test")