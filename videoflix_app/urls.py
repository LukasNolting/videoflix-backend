from django.urls import include, path
from videoflix_app.views import LoginView, RegisterView, VideoView



urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('videos/', VideoView.as_view(), name='video-detail'),
    path('signup/', RegisterView.as_view(), name='signup'),
]
