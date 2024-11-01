import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.core.files import File
from videoflix_app.models import User, Video, PasswordReset, UserFavoriteVideo, UserContinueWatchVideo
from videoflix_app.tasks import convert_video_to_hls, process_video
from unittest.mock import patch
import tempfile

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token

@pytest.fixture
def authenticated_client(api_client, token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client

@pytest.fixture
def video(db):
    return Video.objects.create(
        title="Test Video",
        description="This is a test video",
        category="action",
        created_at=timezone.now()
    )

@pytest.fixture
def video_with_file(db):
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
        video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            video_file=File(temp_file, name="test_video.mp4")
        )
        yield video  # Gibt das Video zurück, solange der temporäre File existiert

# User Tests
@pytest.mark.django_db
def test_create_user(api_client):
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpassword123',
        'remember': True
    }
    response = api_client.post(reverse('signup'), data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_login_user(api_client, user):
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = api_client.post(reverse('login'), data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data

@pytest.mark.django_db
def test_invalid_login(api_client, user):
    data = {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    response = api_client.post(reverse('login'), data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Video Tests
@pytest.mark.django_db
def test_video_list(authenticated_client):
    response = authenticated_client.get(reverse('video_detail'))
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

@pytest.mark.django_db
def test_video_detail(authenticated_client):
    response = authenticated_client.get(reverse('video_detail'))
    assert response.status_code == status.HTTP_200_OK

# Password Reset Tests
@pytest.mark.django_db
def test_password_reset_request_valid_email(api_client, user):
    response = api_client.post(reverse('password_reset'), {'email': 'test@example.com'}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'success' in response.data

@pytest.mark.django_db
def test_password_reset_request_invalid_email(api_client):
    response = api_client.post(reverse('password_reset'), {'email': 'invalid@example.com'}, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_password_reset_token_valid(api_client, user):
    token = PasswordReset.objects.create(email='test@example.com', token='validtoken')
    response = api_client.get(reverse('password_reset_token', kwargs={'token': token.token}))
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_password_reset_token_invalid(api_client):
    response = api_client.get(reverse('password_reset_token', kwargs={'token': 'invalidtoken'}))
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Favorite Video Tests
@pytest.mark.django_db
def test_toggle_favorite(authenticated_client, user, video):
    response = authenticated_client.post(reverse('toggle_favorite'), {'video_id': video.id}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert UserFavoriteVideo.objects.filter(user=user, video=video, is_favorite=True).exists()

# Continue Watching Tests
@pytest.mark.django_db
def test_continue_watching_list(authenticated_client, user, video):
    UserContinueWatchVideo.objects.create(user=user, video=video, timestamp=120.5)
    response = authenticated_client.get(reverse('continue_watch'))
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_delete_continue_watching(authenticated_client, user, video):
    UserContinueWatchVideo.objects.create(user=user, video=video, timestamp=120.5)
    response = authenticated_client.delete(reverse('continue_watch'), {'video_id': video.id}, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserContinueWatchVideo.objects.filter(user=user, video=video).exists()

# Task Tests
@pytest.mark.django_db
@patch('videoflix_app.tasks.subprocess.run')
def test_convert_video_to_hls_success(mock_run, video_with_file):
    mock_run.return_value.returncode = 0
    result = convert_video_to_hls(video_with_file.video_file.path)
    assert result is None

@pytest.mark.django_db
@patch('videoflix_app.tasks.convert_video_to_hls')
@patch('os.path.exists')
def test_process_video_success(mock_exists, mock_convert, video_with_file):
    mock_exists.return_value = True
    mock_convert.return_value = None
    process_video(video_with_file)
    mock_convert.assert_called_once_with(video_with_file.video_file.path)