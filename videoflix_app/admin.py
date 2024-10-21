from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html

from .models import Video, User, PasswordReset, UserFavoriteVideo, UserContinueWatchVideo


# Resource für Video-Modell (für den Import/Export)
class VideoResource(resources.ModelResource):
    class Meta:
        model = Video


# Admin-Konfiguration für das Video-Modell
@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    resource_class = VideoResource
    list_display = ('title', 'category', 'created_at', 'video_thumbnail')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')

    # Thumbnail in der Admin-Liste anzeigen
    def video_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.thumbnail.url))
        return "No Thumbnail"
    video_thumbnail.short_description = 'Thumbnail'


# Admin-Konfiguration für das User-Modell
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'remember', 'is_staff')
    list_filter = ('is_active', 'remember', 'is_staff')
    search_fields = ('email', 'username', 'is_active', 'remember', 'is_staff')
    ordering = ('email',)


# Admin-Konfiguration für das PasswordReset-Modell
@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at')
    search_fields = ('email', 'token')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


# Admin-Konfiguration für das UserFavoriteVideo-Modell
@admin.register(UserFavoriteVideo)
class UserFavoriteVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'is_favorite', 'created_at')
    list_filter = ('is_favorite', 'created_at')
    search_fields = ('user__email', 'video__title')
    ordering = ('-created_at',)


# Admin-Konfiguration für das UserContinueWatchVideo-Modell
@admin.register(UserContinueWatchVideo)
class UserContinueWatchVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'timestamp', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'video__title')
    ordering = ('-created_at',)

