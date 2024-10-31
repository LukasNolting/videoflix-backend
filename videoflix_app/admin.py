from django.contrib import admin
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Video, User, PasswordReset, UserFavoriteVideo, UserContinueWatchVideo


class VideoResource(resources.ModelResource):
    class Meta:
        model = Video

@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    resource_class = VideoResource
    list_display = ('title', 'category', 'created_at', 'video_thumbnail')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')

    def video_thumbnail(self, obj):
        """
        Returns an HTML image tag with the video's thumbnail if available,
        otherwise returns a text indicating no thumbnail is available.

        :param obj: The Video object.
        :return: An HTML string representing the thumbnail or a "No Thumbnail" text.
        """
        if obj.thumbnail:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.thumbnail.url))
        return "No Thumbnail"
    video_thumbnail.short_description = 'Thumbnail'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'remember', 'is_staff')
    list_filter = ('is_active', 'remember', 'is_staff')
    search_fields = ('email', 'username', 'is_active', 'remember', 'is_staff')
    ordering = ('email',)

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at')
    search_fields = ('email', 'token')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserFavoriteVideo)
class UserFavoriteVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'is_favorite', 'created_at')
    list_filter = ('is_favorite', 'created_at')
    search_fields = ('user__email', 'video__title')
    ordering = ('-created_at',)

@admin.register(UserContinueWatchVideo)
class UserContinueWatchVideoAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'timestamp', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'video__title')
    ordering = ('-created_at',)