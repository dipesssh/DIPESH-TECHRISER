# tests.py for the home app
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from home.models import Blog, Comment
from rest_framework_simplejwt.tokens import RefreshToken
from io import BytesIO
from PIL import Image

def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

def create_test_image():
    image = Image.new('RGB', (100, 100), color='red')
    temp_file = BytesIO()
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    
    return SimpleUploadedFile(
        name='test.jpg',
        content=temp_file.read(),
        content_type='image/jpeg'
    )

class BlogTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="johndoe", password="test12345")
        self.token = generate_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_blog(self):
        url = '/api/home/blog/'
        data = {
            "title": "Test Blog",
            "blog_text": "This is a test blog.",
            "main_image": create_test_image()
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_blogs(self):
        Blog.objects.create(user=self.user, title="B1", blog_text="Hello", main_image=create_test_image())
        response = self.client.get('/api/home/blog/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_update_blog(self):
        blog = Blog.objects.create(user=self.user, title="Old", blog_text="Old", main_image=create_test_image())
        data = {
            "uid": str(blog.uid),
            "title": "Updated Title"
        }
        response = self.client.patch('/api/home/blog/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], "Updated Title")

    def test_delete_blog(self):
        blog = Blog.objects.create(user=self.user, title="Delete", blog_text="Bye", main_image=create_test_image())
        data = {"uid": str(blog.uid)}
        response = self.client.delete('/api/home/blog/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CommentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="jane", password="password")
        self.token = generate_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.blog = Blog.objects.create(user=self.user, title="Blog", blog_text="Text", main_image=create_test_image())

    def test_post_comment(self):
        url = f'/api/home/blog/{self.blog.uid}/comments/'
        data = {"text": "Nice blog!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], "Nice blog!")

    def test_get_comments(self):
        Comment.objects.create(user=self.user, blog=self.blog, text="Test comment")
        url = f'/api/home/blog/{self.blog.uid}/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
