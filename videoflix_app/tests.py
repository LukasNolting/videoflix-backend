from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from videoflix_app.models import User

class UserTestCase(TestCase):
    def setUp(self):
        # Erstelle einen Benutzer und aktiviere ihn
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


from django.utils import timezone
from videoflix_app.models import Video
from rest_framework.authtoken.models import Token

class VideoTestCase(TestCase):
    def setUp(self):
        # Erstelle einen Benutzer und aktiviere ihn
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.user.is_active = True
        self.user.save()

        # Erstelle den APIClient und den Token
        self.client = APIClient()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Erstelle ein Test-Video
        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video",
            category="action",
            created_at=timezone.now()
        )

    def test_video_list(self):
        response = self.client.get(reverse('video_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)

    def test_video_detail(self):
        response = self.client.get(reverse('video_detail', kwargs={'pk': self.video.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
