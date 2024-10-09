"""
URL configuration for videoflix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('videoflix/admin/', admin.site.urls),
    path('videoflix/__debug__/', include('debug_toolbar.urls')),
    path('videoflix/', include('videoflix_app.urls')),
<<<<<<< HEAD
] 
# Adding static files URL patterns
urlpatterns += staticfiles_urlpatterns()

# Adding media files URL patterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
    path('videoflix/rq/', include('django_rq.urls')),
] + staticfiles_urlpatterns()

>>>>>>> fc7d91b1cafca1920b6a0538245ef6a93075850f
