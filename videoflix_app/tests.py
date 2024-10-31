from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from videoflix_app.models import User, Video, PasswordReset, UserFavoriteVideo, UserContinueWatchVideo
from videoflix_app.functions import activate_user, favorite_videos, user_continue_watching
from videoflix_app.tasks import convert_video_to_hls, process_video
import os

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = True
        self.user.save()
        self.client = APIClient()

    def test_create_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'remember': True
        }
        response = self.client.post(reverse('signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class VideoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = True
        self.user.save()

        self.client = APIClient()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            created_at=timezone.now()
        )

    def test_video_list(self):
        response = self.client.get(reverse('video_detail'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIsInstance(response_data, list)

    def test_video_detail(self):
        response = self.client.get(reverse('video_detail'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.client = APIClient()

    def test_password_reset_request_valid_email(self):
        response = self.client.post(reverse('password_reset'), {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    def test_password_reset_request_invalid_email(self):
        response = self.client.post(reverse('password_reset'), {'email': 'invalid@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_token_valid(self):
        token = PasswordReset.objects.create(email='test@example.com', token='validtoken')
        response = self.client.get(reverse('password_reset_token', kwargs={'token': token.token}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_token_invalid(self):
        response = self.client.get(reverse('password_reset_token', kwargs={'token': 'invalidtoken'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class FavoriteVideoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = True
        self.user.save()
        self.client = APIClient()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            created_at=timezone.now()
        )

    def test_toggle_favorite(self):
        response = self.client.post(reverse('toggle_favorite'), {'video_id': self.video.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserFavoriteVideo.objects.filter(user=self.user, video=self.video, is_favorite=True).exists())

class ContinueWatchingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = True
        self.user.save()
        self.client = APIClient()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            created_at=timezone.now()
        )

    def test_continue_watching_list(self):
        UserContinueWatchVideo.objects.create(user=self.user, video=self.video, timestamp=120.5)
        response = self.client.get(reverse('continue_watch'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_continue_watching(self):
        UserContinueWatchVideo.objects.create(user=self.user, video=self.video, timestamp=120.5)
        response = self.client.delete(reverse('continue_watch'), {'video_id': self.video.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserContinueWatchVideo.objects.filter(user=self.user, video=self.video).exists())

class FunctionsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = False
        self.user.save()
        self.factory = RequestFactory()

class TasksTestCase(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            video_file='path/to/video.mp4'
        )

    @patch('videoflix_app.tasks.subprocess.run')
    def test_convert_video_to_hls_success(self, mock_run):
        mock_run.return_value.returncode = 0
        result = convert_video_to_hls(self.video.video_file.path)
        self.assertIsNone(result)

    @patch('videoflix_app.tasks.convert_video_to_hls')
    @patch('os.path.exists')
    def test_process_video_success(self, mock_exists, mock_convert):
        mock_exists.return_value = True
        mock_convert.return_value = None
        process_video(self.video)
        mock_convert.assert_called_once_with(self.video.video_file.path)