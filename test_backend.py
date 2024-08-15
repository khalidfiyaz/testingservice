import unittest
from unittest.mock import patch, MagicMock
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

if __name__ == '__main__':
    unittest.main()
