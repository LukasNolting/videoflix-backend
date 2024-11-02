from django.urls import path, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path('videoflix/admin/', admin.site.urls),
    # path('videoflix/__debug__/', include('debug_toolbar.urls')),
    path('videoflix/', include('videoflix_app.urls')),
]