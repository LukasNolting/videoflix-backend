from django.urls import include, path
from videoflix_app.views import LoginView, RegisterView, VideoView
from videoflix_app.views import activate_user



urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('videos/', VideoView.as_view(), name='video-detail'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', activate_user, name='activate_user'),
]
