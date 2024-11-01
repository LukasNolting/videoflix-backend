from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('videoflix/admin/', admin.site.urls),
    # path('videoflix/__debug__/', include('debug_toolbar.urls')),
    path('videoflix/', include('videoflix_app.urls')),
] 

urlpatterns += staticfiles_urlpatterns()

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)