from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import User  # Remplacez par les modèles appropriés
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import pandas as pd
from io import StringIO
from prbmg import settings
import pytest
import requests_mock
from unittest import mock
from clustering.views import process_clustering 


class HomeViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the home view.
        
        - Initializes the test client
        - Sets the URL for the home view
        """
        self.client = Client()
        self.url = reverse('home')

    def test_home_view_status_code(self):
        """
        Test the HTTP status code for the home view.
        
        - Asserts that the home view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """
        Test the template used by the home view.
        
        - Asserts that the home view uses the 'home.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'home.html')


class LoginViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the login view.
        
        - Initializes the test client
        - Creates a user for testing
        - Sets the URL for the login view
        """
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_login_view_status_code(self):
        """
        Test the HTTP status code for the login view.
        
        - Asserts that the login view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_template(self):
        """
        Test the template used by the login view.
        
        - Asserts that the login view uses the 'login.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_with_valid_credentials(self):
        """
        Test login with valid credentials.
        
        - Asserts that the user is redirected to the home page upon successful login
        """
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'password'})
        self.assertRedirects(response, reverse('home'))

    def test_login_view_with_invalid_credentials(self):
        """
        Test login with invalid credentials.
        
        - Asserts that an error message is displayed for invalid credentials
        """
        response = self.client.post(self.url, {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertContains(response, 'Invalid password or username')


class LogoutViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the logout view.
        
        - Initializes the test client
        - Creates and logs in a user for testing
        - Sets the URL for the logout view
        """
        self.client = Client()
        self.url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_logout_view(self):
        """
        Test the logout functionality.
        
        - Asserts that the user is redirected to the home page after logout
        - Asserts that the user session is cleared after logout
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session)


class SignupViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the signup view.
        
        - Initializes the test client
        - Sets the URL for the signup view
        """
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_view_status_code(self):
        """
        Test the HTTP status code for the signup view.
        
        - Asserts that the signup view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_view_template(self):
        """
        Test the template used by the signup view.
        
        - Asserts that the signup view uses the 'signup.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_view_valid_form(self):
        """
        Test signup with a valid form.
        
        - Asserts that a new user is created and redirected to the home page upon successful signup
        """
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
        """
        Set up the test environment for the user update view.
        
        - Initializes the test client
        - Creates and logs in a user for testing
        - Sets the URL for the update user view
        """
        self.client = Client()
        self.url = reverse('update_user')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_update_user_view_status_code(self):
        """
        Test the HTTP status code for the update user view.
        
        - Asserts that the update user view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_update_user_view_template(self):
        """
        Test the template used by the update user view.
        
        - Asserts that the update user view uses the 'update_user.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'update_user.html')

    def test_update_user_view_valid_form(self):
        """
        Test user update with a valid form.
        
        - Asserts that user details are updated and redirected to the update user view upon successful form submission
        """
        response = self.client.post(self.url, {
            'username': 'updateduser',
            'email': 'updateduser@example.com'
        })
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')


class UploadFileViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the file upload view.
        
        - Initializes the test client
        - Creates and logs in a user for testing
        - Sets the URL for the file upload view
        """
        self.client = Client()
        self.url = reverse('clustering')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_upload_file_view_status_code(self):
        """
        Test the HTTP status code for the file upload view.
        
        - Asserts that the file upload view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_upload_file_view_template(self):
        """
        Test the template used by the file upload view.
        
        - Asserts that the file upload view uses the 'upload.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'upload.html')

    def test_upload_file_view_valid_file(self):
        """
        Test file upload with a valid CSV file.
        
        - Asserts that the file upload is successful and a success message is displayed
        """
        csv_content = "incident_number,Origin of Request,Requesting Person,description,category_full,ci_name,location_full, creation_date\n" \
                      "1,Monitoring,REST API - ZABBIX,Test description,Test category,Test CI,Test Location, Test date"
        file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'), content_type="text/csv")
        response = self.client.post(self.url, {'file': file})
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File uploaded successfully')


class DownloadFileViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the file download view.
        
        - Initializes the test client
        - Creates and logs in a user for testing
        - Creates a test file for download
        """
        self.client = Client()
        self.url = reverse('download_file', args=['testfile.csv'])
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.file_path = os.path.join(settings.MEDIA_ROOT, 'testfile.csv')
        with open(self.file_path, 'w') as file:
            file.write("sample data")

    def tearDown(self):
        """
        Clean up after tests.
        
        - Removes the test file if it exists
        """
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_download_file_view(self):
        """
        Test file download functionality.
        
        - Asserts that the file download returns a status code of 200
        - Asserts that the 'Content-Disposition' header indicates a file attachment
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=testfile.csv')


class DashboardPredictionsViewTests(TestCase):
    def setUp(self):
        """
        Set up the test environment for the dashboard predictions view.
        
        - Initializes the test client
        - Creates and logs in a user for testing
        - Sets the URL for the dashboard predictions view
        """
        self.client = Client()
        self.url = reverse('dashboard_predictions')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_dashboard_predictions_view_status_code(self):
        """
        Test the HTTP status code for the dashboard predictions view.
        
        - Asserts that the dashboard predictions view returns a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_predictions_view_template(self):
        """
        Test the template used by the dashboard predictions view.
        
        - Asserts that the dashboard predictions view uses the 'dashboard_predictions.html' template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'dashboard_predictions.html')

    def test_dashboard_predictions_view_data(self):
        """
        Test the context data provided by the dashboard predictions view.
        
        - Asserts that the context contains 'predictions' and 'data_points'
        """
        response = self.client.get(self.url)
        self.assertIn('predictions', response.context)
        self.assertIn('data_points', response.context)


class ClusteringViewsTests(TestCase):
    @mock.patch.dict(os.environ, {"API_IA_SECRET_KEY": "test_secret_key"})
    @requests_mock.Mocker()  # Utilisation de requests_mock pour simuler les requêtes HTTP
    def test_process_clustering(self, mock_request):
        """
        Test the `process_clustering` function to ensure it correctly processes a DataFrame of incidents and handles API responses.

        This test performs the following checks:
        
        1. **Simulates an API Response**: Uses `requests_mock` to mock an API endpoint (`/predict`) and returns a sample response containing a `cluster_number` and `problem_title`.
        
        2. **Tests DataFrame Processing**: Creates a test DataFrame with incident data and calls the `process_clustering` function to update the DataFrame based on the mocked API response. Verifies that the DataFrame is updated correctly with the `cluster_number` and `problem_title`.

        3. **Verifies API Request**: Ensures that the API request was made with the expected data and that it was called exactly once.

        4. **Simulates API Error**: Simulates an API error response with a status code of 500, and checks that the `process_clustering` function handles the error by updating the DataFrame with appropriate error messages.

        Args:
            self: The test case instance.
            mock_request: A `requests_mock.Mocker` instance used to mock HTTP requests.

        Returns:
            None. The function uses assertions to verify that the `process_clustering` function behaves as expected.
        """
        # Simuler l'URL de l'API avec requests_mock
        api_url = "http://prbmg-api-ia.francecentral.azurecontainer.io:8001/predict"
        mock_request.post(api_url, json={
            "cluster_number": 123,
            "problem_title": "Sample Problem Title"
        })

        # Créer un DataFrame de test
        data = {
            'incident_number': ['1234'],
            'creation_date': ['2023-04-23 08:34'],
            'description': ["Trigger: Host has been restarted..."],
            'category_full': ['Incidents/Infrastructure/System/RDS'],
            'ci_name': ['S273A12'],
            'location_full': ['INDIA/INDIA/MUMBAI']
        }
        df = pd.DataFrame(data)

        # Appeler la fonction de clustering
        updated_df = process_clustering(df)

        # Vérifier que les colonnes ont été correctement mises à jour
        self.assertEqual(updated_df.at[0, 'cluster_number'], 123)
        self.assertEqual(updated_df.at[0, 'problem_title'], "Sample Problem Title")

        # Vérifier que la requête à l'API a bien été faite
        expected_request_data = {
            'incident_number': '1234',
            'creation_date': '2023-04-23 08:34',
            'description': "Trigger: Host has been restarted...",
            'category_full': 'Incidents/Infrastructure/System/RDS',
            'ci_name': 'S273A12',
            'location_full': 'INDIA/INDIA/MUMBAI'
        }

        self.assertTrue(mock_request.called_once)
        self.assertEqual(mock_request.request_history[0].json(), expected_request_data)

        # Simuler une réponse d'erreur de l'API
        mock_request.post(api_url, status_code=500)
        df = pd.DataFrame(data)  # Recréer un DataFrame propre pour le test suivant
        updated_df = process_clustering(df)

        # Vérifier que les colonnes contiennent l'information d'erreur
        self.assertEqual(updated_df.at[0, 'cluster_number'], 'Error')
        self.assertEqual(updated_df.at[0, 'problem_title'], f"Error for incident 1234")
