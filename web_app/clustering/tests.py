from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import User  # Remplacez par les modèles appropriés
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import pandas as pd
from io import StringIO
from prbmg import settings


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('home')

    def test_home_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'home.html')


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_login_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_with_valid_credentials(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'password'})
        self.assertRedirects(response, reverse('home'))

    def test_login_view_with_invalid_credentials(self):
        response = self.client.post(self.url, {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertContains(response, 'Invalid password or username')


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_logout_view(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session)


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_view_valid_form(self):
        response = self.client.post(self.url, {
            'username': 'newuser',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
            'email': 'newuser@example.com'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())


class UpdateUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('update_user')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_update_user_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_update_user_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'update_user.html')

    def test_update_user_view_valid_form(self):
        response = self.client.post(self.url, {
            'username': 'updateduser',
            'email': 'updateduser@example.com'
        })
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')


class UploadFileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('clustering')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_upload_file_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_upload_file_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'upload.html')

    def test_upload_file_view_valid_file(self):
        csv_content = "incident_number,Origin of Request,Requesting Person,description,category_full,ci_name,location_full, creation_date\n" \
                      "1,Monitoring,REST API - ZABBIX,Test description,Test category,Test CI,Test Location, Test date"
        file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'), content_type="text/csv")
        response = self.client.post(self.url, {'file': file})
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File uploaded successfully')


class DownloadFileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('download_file', args=['testfile.csv'])
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.file_path = os.path.join(settings.MEDIA_ROOT, 'testfile.csv')
        with open(self.file_path, 'w') as file:
            file.write("sample data")

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_download_file_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=testfile.csv')


class DashboardPredictionsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('dashboard_predictions')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_dashboard_predictions_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_predictions_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'dashboard_predictions.html')

    def test_dashboard_predictions_view_data(self):
        response = self.client.get(self.url)
        self.assertIn('predictions', response.context)
        self.assertIn('data_points', response.context)





