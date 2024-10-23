from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from videoflix_app.models import User, Video, PasswordReset
from rest_framework.authtoken.models import Token

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="password123"
        )
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_user(self):
        data = {
            'username': 'newuser', 
            'email': 'new@example.com', 
            'password': 'newpassword123', 
            'remember': True
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        data = {
            'email': 'test@example.com', 
            'password': 'password123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        data = {
            'email': 'test@example.com', 
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VideoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="password123"
        )
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
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
        self.assertEqual(len(response.data), 1)

    def test_video_detail(self):
        response = self.client.get(reverse('video_detail'), {'id': self.video.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class FavoriteVideoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="password123"
        )
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.video = Video.objects.create(
            title="Test Video", 
            description="This is a test video", 
            category="action",
            created_at=timezone.now()
        )

    def test_add_favorite_video(self):
        data = {'video_id': self.video.id}
        response = self.client.post(reverse('toggle_favorite'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_favorite_videos(self):
        response = self.client.get(reverse('toggle_favorite'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="password123"
        )
        self.client = APIClient()

    def test_password_reset_request(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(reverse('password_reset'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_invalid_email(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(reverse('password_reset'), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_token_validation(self):
        # Assuming you've created a token for this user during setup
        token = PasswordReset.objects.create(email=self.user.email, token='valid_token')
        response = self.client.get(reverse('password_reset_token', kwargs={'token': 'valid_token'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password_reset_token(self):
        response = self.client.get(reverse('password_reset_token', kwargs={'token': 'invalid_token'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
