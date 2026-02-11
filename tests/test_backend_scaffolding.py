"""
Integration tests for the backend scaffolding.

Tests cover:
- Flask app creation and initialization
- Benchmark loading on startup
- /api/chat endpoint with mocked AI
- Error handling and logging
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from app.main import create_app
from app.database.models import UserProfile
from app.logger import get_logger


class TestAppCreation(unittest.TestCase):
    """Test Flask app creation and initialization."""
    
    def test_create_app_returns_flask_app(self):
        """Test that create_app returns a Flask application."""
        app = create_app()
        
        self.assertIsNotNone(app)
        self.assertTrue(hasattr(app, 'route'))  # Flask app has route method
    
    @patch('app.main.load_fitness_benchmarks')
    def test_benchmarks_loaded_on_startup(self, mock_load_benchmarks):
        """Test that benchmarks are loaded when app is created."""
        mock_load_benchmarks.return_value = {'test': 'benchmarks'}
        
        app = create_app()
        
        # Verify benchmarks were loaded
        mock_load_benchmarks.assert_called_once()
        self.assertEqual(app.benchmarks, {'test': 'benchmarks'})
    
    @patch('app.main.load_fitness_benchmarks')
    def test_benchmark_load_failure_raises_error(self, mock_load_benchmarks):
        """Test that app creation fails if benchmark loading fails."""
        mock_load_benchmarks.side_effect = Exception("Benchmark load failed")
        
        with self.assertRaises(Exception):
            create_app()
    
    def test_app_has_database(self):
        """Test that app is configured with database."""
        app = create_app()
        
        self.assertIn('SQLALCHEMY_DATABASE_URI', app.config)
        self.assertIn('users.db', app.config['SQLALCHEMY_DATABASE_URI'])
    
    def test_app_has_secret_key(self):
        """Test that app has a secret key configured."""
        app = create_app()
        
        self.assertIsNotNone(app.config['SECRET_KEY'])


class TestChatAPIEndpoint(unittest.TestCase):
    """Test /api/chat endpoint functionality."""
    
    def setUp(self):
        """Set up test client."""
        with patch('app.main.load_fitness_benchmarks') as mock_load:
            mock_load.return_value = {}
            self.app = create_app()
            self.client = self.app.test_client()
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_with_message_and_profile(self, mock_ai):
        """Test /api/chat with message and profile."""
        mock_ai.return_value = "Here's your fitness recommendation"
        
        payload = {
            'message': 'How should I exercise?',
            'profile': {
                'name': 'Test User',
                'age': 30,
                'weight': '180 lbs'
            }
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['response'], "Here's your fitness recommendation")
    
    def test_chat_api_missing_message(self):
        """Test /api/chat without message returns 400."""
        payload = {
            'profile': {'name': 'Test User'}
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_with_minimal_profile(self, mock_ai):
        """Test /api/chat with minimal profile data."""
        mock_ai.return_value = "General fitness advice"
        
        payload = {
            'message': 'Help with fitness',
            'profile': {}
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], "General fitness advice")
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_creates_user_profile(self, mock_ai):
        """Test that /api/chat creates UserProfile from request."""
        mock_ai.return_value = "Response"
        
        payload = {
            'message': 'Test',
            'profile': {
                'name': 'Alice',
                'age': 25,
                'gender': 'female',
                'fitness_goals': ['endurance']
            }
        }
        
        self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Verify AI was called with UserProfile
        mock_ai.assert_called_once()
        call_args = mock_ai.call_args
        profile_arg = call_args[1]['profile']
        
        self.assertIsInstance(profile_arg, UserProfile)
        self.assertEqual(profile_arg.name, 'Alice')
        self.assertEqual(profile_arg.age, 25)
        self.assertEqual(profile_arg.gender, 'female')
        self.assertIn('endurance', profile_arg.fitness_goals)
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_passes_message_to_ai(self, mock_ai):
        """Test that message is passed to AI recommendation function."""
        mock_ai.return_value = "Response"
        
        test_message = "What's the best workout?"
        payload = {
            'message': test_message,
            'profile': {'name': 'Test'}
        }
        
        self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Verify message was passed
        mock_ai.assert_called_once()
        call_args = mock_ai.call_args
        message_arg = call_args[1]['message']
        
        self.assertEqual(message_arg, test_message)
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_missing_api_key_error(self, mock_ai):
        """Test /api/chat when AI API key is missing."""
        mock_ai.side_effect = ValueError("GEMINI_API_KEY is not set")
        
        payload = {
            'message': 'Test',
            'profile': {'name': 'User'}
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('AI service is not configured', data['error'])
    
    @patch('app.main.get_ai_recommendation')
    def test_chat_api_ai_error_handling(self, mock_ai):
        """Test /api/chat handles AI errors gracefully."""
        mock_ai.side_effect = Exception("API call failed")
        
        payload = {
            'message': 'Test',
            'profile': {'name': 'User'}
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


class TestFrontendRoutes(unittest.TestCase):
    """Test frontend routes."""
    
    def setUp(self):
        """Set up test client."""
        with patch('app.main.load_fitness_benchmarks') as mock_load:
            mock_load.return_value = {}
            self.app = create_app()
            self.client = self.app.test_client()
    
    def test_index_route_accessible(self):
        """Test that / route is accessible."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_chat_route_accessible(self):
        """Test that /chat route is accessible."""
        response = self.client.get('/chat')
        
        self.assertEqual(response.status_code, 200)


class TestIntegrationFlow(unittest.TestCase):
    """Test complete integration flow."""
    
    def setUp(self):
        """Set up test client."""
        with patch('app.main.load_fitness_benchmarks') as mock_load:
            mock_load.return_value = {'strength': {}, 'cardio': {}}
            self.app = create_app()
            self.client = self.app.test_client()
    
    @patch('app.main.get_ai_recommendation')
    def test_full_chat_flow(self, mock_ai):
        """Test complete chat flow from request to response."""
        mock_ai.return_value = "Your personalized fitness plan..."
        
        # Prepare request
        payload = {
            'message': 'Create a fitness plan for me',
            'profile': {
                'name': 'John Doe',
                'age': 30,
                'gender': 'male',
                'height': "5'10\"",
                'weight': '180 lbs',
                'fitness_goals': ['lose weight', 'build strength']
            }
        }
        
        # Send request
        response = self.client.post(
            '/api/chat',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], "Your personalized fitness plan...")
        
        # Verify AI was called correctly
        mock_ai.assert_called_once()
        call_args = mock_ai.call_args
        
        # Check profile
        profile = call_args[1]['profile']
        self.assertEqual(profile.name, 'John Doe')
        self.assertEqual(profile.age, 30)
        self.assertEqual(profile.gender, 'male')
        
        # Check message
        self.assertEqual(call_args[1]['message'], payload['message'])


if __name__ == "__main__":
    unittest.main()
