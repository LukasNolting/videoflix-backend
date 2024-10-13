from django.urls import include, path
from videoflix_app.views import LoginView, RegisterView, VideoView
from videoflix_app.views import activate_user
from .views import RequestPasswordReset, PasswordResetView, favorite_videos

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('videos/', VideoView.as_view(), name='video_detail'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', activate_user, name='activate_user'),
    path('password-reset/', RequestPasswordReset.as_view(), name='password_reset'),
    path('password-reset/<token>/', PasswordResetView.as_view(), name='password_reset_token'),
    path('favorite/', favorite_videos, name='toggle_favorite'),
]