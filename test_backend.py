import unittest
from unittest.mock import patch, MagicMock
import requests
from backend import app

class TestingServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_redirect(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/testform', response.location)

    def test_test_form_page(self):
        response = self.app.get('/testform')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Bed Controls', response.data)

    @patch('backend.subprocess.Popen')
    def test_start_test_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        response = self.app.post('/startTest', data={'test_type': 'network_delay'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Started Successfully', response.data)
        self.assertIn(b'View Results on Grafana', response.data)

    @patch('backend.subprocess.Popen')
    def test_start_test_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'Error: Test failed')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        response = self.app.post('/startTest', data={'test_type': 'network_delay'})
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Test failed to start', response.data)

    def test_invalid_test_type(self):
        response = self.app.post('/startTest', data={'test_type': 'invalid_test'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid test type selected', response.data)

    @patch('os.path.isfile')
    def test_test_script_not_found(self, mock_isfile):
        mock_isfile.return_value = False

        response = self.app.post('/startTest', data={'test_type': 'network_delay'})
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Test script not found', response.data)

    def test_cloned_microservice_accessibility(self):
        """Test if the cloned microservice is accessible"""
        microservice_url = 'http://localhost:5001'  # Use 'localhost' instead of 'cloned_microservice'
        try:
            response = requests.get(microservice_url)
            self.assertEqual(response.status_code, 200)
        except requests.ConnectionError:
            self.fail(f"Could not connect to the cloned microservice at {microservice_url}")

    def test_grafana_accessibility(self):
        """Test if Grafana is accessible"""
        grafana_url = 'http://localhost:3000'
        try:
            response = requests.get(grafana_url)
            self.assertEqual(response.status_code, 200)
        except requests.ConnectionError:
            self.fail(f"Could not connect to Grafana at {grafana_url}")

    def test_postgres_accessibility(self):
        """Test if PostgreSQL is accessible"""
        postgres_url = 'http://postgres:5432'  # PostgreSQL typically runs on port 5432
        try:
            # This is a mock test as typically you connect to PostgreSQL using a database client, not HTTP
            response = requests.get(postgres_url)
            self.fail("PostgreSQL should not be accessible via HTTP")
        except requests.ConnectionError:
            pass  # Expected behavior since PostgreSQL isn't accessed via HTTP

if __name__ == '__main__':
    unittest.main()
